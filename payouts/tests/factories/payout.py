import factory

from factory.fuzzy import FuzzyDecimal

from ...models import Payout
from ...choices import CurrencyChoices, PayoutStatus


class PayoutFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payout

    amount = FuzzyDecimal(500.5, 1000.7, 2)

    currency = CurrencyChoices.RUB
    recipient_details = {
        'card_number': '1234567812345678'
    }
    status = PayoutStatus.PENDING
    comment = 'Test payout comment'
