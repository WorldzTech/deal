from pathlib import Path

SECRET_KEY = 'django-insecure-ub8r!xasdw@erf34xdvbdfc)nkxh(@cl2(m73_a#j7upav1qfh!vw'

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'deal',
        'USER': 'deal_admin',
        'PASSWORD': 'Red159753tie!',
        'HOST': '77.222.54.31',
        'PORT': '5432',
    }
}