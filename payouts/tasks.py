import time
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import DatabaseError, InterfaceError

from .constants import TASK_RESULT_TIMEOUT, TASK_RESULT_NOT_FOUND, TASK_RESULT_SUCCESS
from .exceptions import GatewayTimeoutError, PayoutNotFoundError
from .models import Payout
from .choices import PayoutStatus


logger = get_task_logger(__name__)


@shared_task(bind=True)
def process_payout_task(self, payout_id: str) -> str:
    logger.info(f'Starting processing payout: {payout_id}')

    try:
        try:
            payout: Payout = Payout.objects.get(id=payout_id)
        except Payout.DoesNotExist:
            raise PayoutNotFoundError(f'Payout {payout_id} not found')

        payout.status = PayoutStatus.PROCESSING
        payout.save(update_fields=('status', 'updated_at'))
        logger.info(f'Payout {payout_id} status: PROCESSING')

        delay: int = settings.PAYOUT_GATEWAY_DELAY
        timeout: int = settings.PAYOUT_PROCESSING_TIMEOUT

        logger.info(f'Waiting for gateway response ({delay}s)...')
        time.sleep(delay)

        if delay > timeout:
            raise GatewayTimeoutError(
                f'Gateway timeout: {delay}s > {timeout}s'
            )

        payout.status = PayoutStatus.SUCCESS
        payout.comment = f'Successfully processed in {delay}s'
        payout.save(update_fields=('status', 'comment', 'updated_at'))

        logger.info(f'Payout {payout_id} status: SUCCESS')
        return TASK_RESULT_SUCCESS

    except PayoutNotFoundError as exc:
        logger.error(str(exc))
        return TASK_RESULT_NOT_FOUND

    except GatewayTimeoutError as exc:
        payout.status = PayoutStatus.FAILED
        payout.comment = str(exc)
        payout.save(update_fields=('status', 'comment', 'updated_at'))

        logger.info(f'Payout {payout_id} status: FAILED (Timeout)')
        return TASK_RESULT_TIMEOUT

    except (DatabaseError, InterfaceError) as exc:
        logger.error(f'Database error for {payout_id}: {exc}', exc_info=True)
        raise self.retry(
            exc=exc,
            max_retries=settings.PAYOUT_TASK_MAX_RETRIES,
            countdown=settings.PAYOUT_TASK_RETRY_DELAY
        )

    except Exception as exc:
        logger.error(f'Unexpected error for {payout_id}: {exc}', exc_info=True)
        raise self.retry(
            exc=exc,
            max_retries=settings.PAYOUT_TASK_MAX_RETRIES,
            countdown=settings.PAYOUT_TASK_RETRY_DELAY
        )
