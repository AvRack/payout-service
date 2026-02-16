import re
from typing import Any

from rest_framework import serializers

from ..models import Payout
from ..choices import PayoutStatus, CurrencyChoices
from ..constants import FINAL_PAYOUT_STATUSES, MIN_PAYOUT_AMOUNT


class PayoutSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=MIN_PAYOUT_AMOUNT,
        help_text=f'Минимальная сумма: {MIN_PAYOUT_AMOUNT}',
        error_messages={
            'min_value': f'Сумма выплаты должна быть не менее {MIN_PAYOUT_AMOUNT}.',
            'invalid': 'Введите корректное число.',
        }
    )

    currency = serializers.ChoiceField(
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.RUB
    )

    comment = serializers.CharField(
        max_length=255,
        allow_blank=True,
        allow_null=True,
        required=False,
        help_text='Максимум 255 символов'
    )

    status = serializers.ChoiceField(
        choices=PayoutStatus.choices,
        read_only=True
    )

    class Meta:
        model = Payout
        fields = (
            'id',
            'amount',
            'currency',
            'recipient_details',
            'status',
            'comment',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_recipient_details(self, value: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise serializers.ValidationError('Реквизиты должны быть JSON-объектом.')

        card_number: Any = value.get('card_number')
        if not card_number:
            raise serializers.ValidationError({'card_number': 'Номер карты обязателен.'})

        clean_card: str = str(card_number).replace(' ', '')
        if not re.fullmatch(r'\d{16}', clean_card):
            raise serializers.ValidationError({'card_number': 'Номер карты должен состоять из 16 цифр.'})

        return value

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.instance and self.instance.status in FINAL_PAYOUT_STATUSES:
            raise serializers.ValidationError(
                f'Заявка в статусе {self.instance.status} закрыта для редактирования.'
            )
        return data
