import os


ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')


if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'dev':
    try:
        from .local import *
    except ImportError:
        from .dev import *
