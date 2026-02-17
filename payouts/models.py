import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from payouts.choices import CurrencyChoices, PayoutStatus
from payouts.constants import MIN_PAYOUT_AMOUNT


class Payout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(MIN_PAYOUT_AMOUNT)],
        verbose_name=_("Сумма выплаты"),
    )
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.RUB,
        verbose_name=_("Валюта"),
    )
    recipient_details = models.JSONField(
        verbose_name=_("Реквизиты получателя"),
        help_text=_('Пример: {"card_number": "1234...", "account_id": "408..."}'),
    )
    status = models.CharField(
        max_length=20,
        choices=PayoutStatus.choices,
        default=PayoutStatus.PENDING,
        verbose_name=_("Статус"),
    )
    comment = models.TextField(max_length=255, blank=True, verbose_name=_("Комментарий"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        verbose_name = _("Выплата")
        verbose_name_plural = _("Выплаты")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Payout {self.id} ({self.amount} {self.currency})"
