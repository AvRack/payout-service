from django.db import models
from django.utils.translation import gettext_lazy as _


class PayoutStatus(models.TextChoices):
    PENDING = "pending", _("В ожидании")
    PROCESSING = "processing", _("В обработке")
    SUCCESS = "success", _("Выполнена")
    FAILED = "failed", _("Ошибка")
    CANCELED = "canceled", _("Отменена")


class CurrencyChoices(models.TextChoices):
    RUB = "RUB", _("Российский рубль")
    USD = "USD", _("Доллар США")
    EUR = "EUR", _("Евро")
