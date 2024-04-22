from pathlib import Path

SECRET_KEY = 'django-insecure-ub8r!xasdw@erf34xdvbdfc)nkxh(@cl2(m73_a#j7upav1qfh!vw'

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}