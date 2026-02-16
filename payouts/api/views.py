import logging
from typing import Any

from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from ..models import Payout
from .serializers import PayoutSerializer
from ..tasks import process_payout_task


logger = logging.getLogger(__name__)


class PayoutViewSet(viewsets.ModelViewSet):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer
    lookup_field = 'id'

    def perform_create(self, serializer: PayoutSerializer) -> None:
        instance = serializer.save()
        logger.info(f'Payout {instance.id} created. Status: {instance.status}')
        try:
            process_payout_task.delay(str(instance.id))
            logger.info(f'Payout {instance.id} sent to Celery worker.')
        except Exception as exc:
            logger.error(f'Could not queue Payout {instance.id}: {exc}', exc_info=True)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance: Payout = self.get_object()
        payout_id = instance.id
        logger.info(f'User {request.user} is deleting Payout {payout_id}')
        self.perform_destroy(instance)
        return Response(
            data={'message': f'Payout {payout_id} successfully deleted'},
            status=status.HTTP_204_NO_CONTENT
        )
