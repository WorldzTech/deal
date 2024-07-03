import os
from pathlib import Path

SECRET_KEY = 'django-insecure-ub8r!xasdw@erf34xdvbdfc)nkxh(@cl2(m73_a#j7upav1qfh!vw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '77.222.53.148', 'deal.api.worldz.tech', '77.222.54.31', 'deal.api.test.worldz.tech']

CSRF_TRUSTED_ORIGINS = ['https://deal.api.worldz.tech', 'https://deal.api.test.worldz.tech', 'https://deal-fashion.com', 'https://admin.deal-fashion.com']

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'deal',
        'USER': 'deal_admin',
        'PASSWORD': 'Red159753tie!',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'applogfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'DEAL.err'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'DEAL': {
            'handlers': ['applogfile', ],
            'level': 'CRITICAL',
        },
    }
}
