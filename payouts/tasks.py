import time

from celery import Task, shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import DatabaseError, InterfaceError

from payouts.choices import PayoutStatus
from payouts.constants import (
    TASK_RESULT_NOT_FOUND,
    TASK_RESULT_SUCCESS,
    TASK_RESULT_TIMEOUT,
)
from payouts.exceptions import GatewayTimeoutError, PayoutNotFoundError
from payouts.models import Payout

logger = get_task_logger(__name__)


@shared_task(bind=True)
def process_payout_task(self: Task, payout_id: str) -> str:
    logger.info("Starting processing payout: %s", payout_id)

    try:
        try:
            payout: Payout = Payout.objects.get(id=payout_id)
        except Payout.DoesNotExist as err:
            msg = f"Payout {payout_id} not found"
            raise PayoutNotFoundError(msg) from err

        payout.status = PayoutStatus.PROCESSING
        payout.save(update_fields=("status", "updated_at"))
        logger.info("Payout %s status: PROCESSING", payout_id)

        delay: int = settings.PAYOUT_GATEWAY_DELAY
        timeout: int = settings.PAYOUT_PROCESSING_TIMEOUT

        logger.info("Waiting for gateway response (%ss)...", delay)
        time.sleep(delay)

        if delay > timeout:
            msg = f"Gateway timeout: {delay}s > {timeout}s"
            raise GatewayTimeoutError(msg) from None

        payout.status = PayoutStatus.SUCCESS
        payout.comment = f"Successfully processed in {delay}s"
        payout.save(update_fields=("status", "comment", "updated_at"))

        logger.info("Payout %s status: SUCCESS", payout_id)
        return TASK_RESULT_SUCCESS

    except PayoutNotFoundError:
        logger.exception("Payout %s not found", payout_id)
        return TASK_RESULT_NOT_FOUND

    except GatewayTimeoutError as exc:
        payout.status = PayoutStatus.FAILED
        payout.comment = str(exc)
        payout.save(update_fields=("status", "comment", "updated_at"))

        logger.info("Payout %s status: FAILED (Timeout)", payout_id)
        return TASK_RESULT_TIMEOUT

    except (DatabaseError, InterfaceError) as exc:
        logger.exception("Database error for %s", payout_id)
        raise self.retry(
            exc=exc,
            max_retries=settings.PAYOUT_TASK_MAX_RETRIES,
            countdown=settings.PAYOUT_TASK_RETRY_DELAY,
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error for %s", payout_id)
        raise self.retry(
            exc=exc,
            max_retries=settings.PAYOUT_TASK_MAX_RETRIES,
            countdown=settings.PAYOUT_TASK_RETRY_DELAY,
        ) from exc
