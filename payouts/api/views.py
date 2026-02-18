import logging
from typing import Any

from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from payouts.api.serializers import PayoutSerializer, PayoutStatusUpdateSerializer
from payouts.models import Payout
from payouts.tasks import process_payout_task

logger = logging.getLogger(__name__)


class PayoutViewSet(viewsets.ModelViewSet):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer
    actions_serializers = {
        "partial_update": PayoutStatusUpdateSerializer,
        "update": PayoutStatusUpdateSerializer,
    }
    lookup_field = "id"

    def get_serializer_class(self):
        return self.actions_serializers.get(self.action, self.serializer_class)

    def perform_create(self, serializer: PayoutSerializer) -> None:
        instance = serializer.save()
        logger.info("Payout %s created. Status: %s", instance.id, instance.status)
        try:
            process_payout_task.delay(str(instance.id))
            logger.info("Payout %s sent to Celery worker.", instance.id)
        except Exception:
            logger.exception("Could not queue Payout %s", instance.id)

    def perform_update(self, serializer: PayoutStatusUpdateSerializer):
        instance = serializer.save()
        logger.info("Payout %s status updated to: %s", instance.id, instance.status)

    def destroy(self, request: Request, *_args: Any, **_kwargs: Any) -> Response:
        instance: Payout = self.get_object()
        payout_id = instance.id
        logger.info("User %s is deleting Payout %s", request.user, payout_id)
        self.perform_destroy(instance)
        return Response(
            data={"message": f"Payout {payout_id} successfully deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )
