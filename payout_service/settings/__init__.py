import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")


if ENVIRONMENT == "production":
    from payout_service.settings.production import *
elif ENVIRONMENT == "dev":
    try:
        from payout_service.settings.local import *
    except ImportError:
        from payout_service.settings.dev import *
