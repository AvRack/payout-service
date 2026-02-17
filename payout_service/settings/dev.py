from django.core.management.utils import get_random_secret_key

from payout_service.settings.base import *

DEBUG = True
SECRET_KEY = get_random_secret_key()
