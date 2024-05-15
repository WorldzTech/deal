from pathlib import Path

SECRET_KEY = 'django-insecure-ub8r!xasdw@erf34xdvbdfc)nkxh(@cl2(m73_a#j7upav1qfh!vw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '77.222.53.148', 'deal.api.worldz.tech']

CSRF_TRUSTED_ORIGINS = ['https://deal.api.worldz.tech']

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
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}