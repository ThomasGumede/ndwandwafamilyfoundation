from pathlib import Path
import os, re
from ndwandwafam.celery_settings import *
from ndwandwafam.logging_config import LOGGING
from decouple import config, Csv
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

IGNORABLE_404_URLS = [
    re.compile(r"^/apple-touch-icon.*\.png$"),
    re.compile(r"^/favicon\.ico$"),
    re.compile(r"^/robots\.txt$"),
]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

TIME_ZONE = 'Africa/Johannesburg'

#  Custom User model
AUTH_USER_MODEL = 'accounts.CustomUserModel'
AUTHENTICATION_BACKENDS = ['accounts.backends.EmailBackend']

LOGIN_URL = 'accounts:login'

YOCO_TEST_MODE = config('YOCO_TEST_MODE')
DEBUG=False
SECRET_KEY='django-insecure-1=5*x6y@4v9_%91v$@183ri9hrw84)-353z8u2c@!!q5^+i)nk'

ADMINS = [('admin@ndwandwa.africa'),( 'support@ndwandwa.africa'), ('gumedethomas12@gmail.com') ]
MANAGERS = [('admin@ndwandwa.africa'), ('support@ndwandwa.africa'), ('gumedethomas12@gmail.com') ]

CSRF_TRUSTED_ORIGINS = ['https://127.0.0.1', 'https://localhost', 'https://ndwandwafam.africa', 'https://www.ndwandwafam.africa', 'https://dashboard.ndwandwafam.africa']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = config('SENDGRIND_API')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_FROM = config('EMAIL_FROM')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('SENDGRIND_API')
EMAIL_PORT = '587'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

if YOCO_TEST_MODE == 1:
    # Yoco
    YOCO_WEBHOOK_KEY = config('YOCO_TEST_WEBHOOK_KEY')
    YOCO_API_KEY = config('YOCO_TEST_API_KEY')
else:
    YOCO_WEBHOOK_KEY = config('YOCO_LIVE_WEBHOOK_KEY')
    YOCO_API_KEY = config('YOCO_LIVE_API_KEY')

if DEBUG:
    ALLOWED_HOSTS=['*']

else:
    ALLOWED_HOSTS=config("ALLOWED_HOSTS",cast=Csv())

    # SSL SETTINGS
    
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ['security.W019']

# Logging
LOGGING


# Application definition

INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',
    'home.apps.HomeConfig',
    'campaigns.apps.CampaignsConfig',
    'events.apps.EventsConfig',
    'payments.apps.PaymentsConfig',
    
    'tailwind',
    'theme',
    'taggit',
    'tinymce',
    'django_celery_beat',
    'django_celery_results',
]

TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = [
    "127.0.0.1", '0.0.0.0'
]
PASSWORD_RESET_TIMEOUT = 14400

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880 # 5MB

TINYMCE_DEFAULT_CONFIG = {
    'theme_advanced_fonts': 'DM Sans=dm-sans,Arial=arial,helvetica,sans-serif',
    'height': "400px",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image charmap print preview anchor searchreplace visualblocks fullscreen insertdatetime media table paste help",
    "toolbar": "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | a11ycheck ltr rtl | showcomments addcomment",
}

TICKETS_PDF_DIR = os.path.join(BASE_DIR, 'media/tickets/pdf')
TICKETS_BARCODE_DIR = os.path.join(BASE_DIR, 'media/tickets/barcodes')
TICKETS_QRCODE_DIR = os.path.join(BASE_DIR, 'media/tickets/qrcodes')

if not os.path.exists(TICKETS_PDF_DIR):
    os.makedirs(TICKETS_PDF_DIR)

if not os.path.exists(TICKETS_BARCODE_DIR):
    os.makedirs(TICKETS_BARCODE_DIR)

if not os.path.exists(TICKETS_QRCODE_DIR):
    os.makedirs(TICKETS_QRCODE_DIR)


NPM_BIN_PATH = "/usr/bin/npm"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ndwandwafam.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'ndwandwafam.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "ndwandwafamdb",
        'USER': config("DB_USER"),
        'PASSWORD': config("DB_PASSWORD"),
        'HOST': config("DB_HOST",'localhost'),
        'PORT': '',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'


USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


STATIC_URL = 'static/'
# STATICFILES_DIRS = [
#     BASE_DIR / 'static_root'
# ]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
