"""
Django settings for lyshop project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY          =  os.environ['LYSHOP_SECRET_KEY']


# SITE NAME SETTING
SITE_NAME           =  os.environ.get('LYSHOP_SITE_NAME', 'LYSHOP')

META_KEYWORDS       = "Lyshop, payment, buy, online-pay, africa-pay, shopping"
META_DESCRIPTION    = "Lyshop is your african solution for online payments"


CELERY_BROKER_URL   = os.environ.get('LYSHOP_CELERY_BROKER_URL')
CELERY_BACKEND      = os.environ.get('LYSHOP_CELERY_BACKEND')

CELERY_DEFAULT_QUEUE = "lyshop-default"
CELERY_DEFAULT_EXCHANGE = "lyshop-default"
CELERY_DEFAULT_ROUTING_KEY = "lyshop-default"

CELERY_OUTGOING_MAIL_QUEUE = "lyshop-outgoing-mails"
CELERY_OUTGOING_MAIL_EXCHANGE = "lyshop-mail"
CELERY_OUTGOING_MAIL_ROUTING_KEY = "lyshop.mail.outgoing"


CELERY_IDENTIFICATION_QUEUE = "lyshop-ident"
CELERY_IDENTIFICATION_EXCHANGE = "lyshop-ident"
CELERY_IDENTIFICATION_ROUTING_KEY = "lyshop.identification"
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'

CELERY_NAMESPACE = 'CELERY'
CELERY_APP_NAME = 'lyshop'
#CELERY_IMPORT = (
#    'dashboard.tasks',
#    'cart.tasks',
#)

ALLOWED_HOSTS = [os.getenv('LYSHOP_ALLOWED_HOST')]

#EMAIL SETTINGS
EMAIL_HOST = os.environ.get('LYSHOP_EMAIL_HOST')
EMAIL_PORT = os.environ.get('LYSHOP_EMAIL_PORT')
EMAIL_HOST_PASSWORD = os.environ.get('LYSHOP_EMAIL_PASSWORD')
EMAIL_HOST_USER = os.environ.get('LYSHOP_EMAIL_USER')
CONTACT_MAIL =  os.environ.get('LYSHOP_CONTACT_MAIL')
EMAIL_USE_SSL = True
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ACCOUNTS = {
    'ACCOUNT_TYPE' :  (
        ('A', 'Admin'),
        ('B', 'Business'),
        ('D', 'Developer'), # create a group Developer instead
        ('I', 'Individual'),
        ('M', 'Manager'), # create a group Manager instead
        ('P', 'Partner'), # create a group Partner instead
        ('S', 'Staff'), # create a group Staff instead

    )
}

VENDOR_PAYMENT_DAY = 5

ACCOUNT_ROOT_PATH = "/accounts/"
HOME_URL = "/"
DASHBOARD_ROOT_PATH = "/dashboard/"
PAYMENT_ROOT_PATH = "/payment/"
VENDOR_ROOT_PATH = "/vendors/"
USER_PATH = "/users/detail/"

PAY_USERNAME = os.getenv('LYSHOP_PAY_USER')
PAY_REQUEST_TOKEN = os.getenv('LYSHOP_PAY_REQUEST_TOKEN')
PAY_REQUEST_DESCRIPTION = os.getenv('LYSHOP_PAY_DESCRIPTION', "LYSHOP PAYMENT")
LYSHOP_USER = os.getenv('LYSHOP_USER')
LYSHOP_FEE_USER = os.getenv('LYSHOP_FEE_USER', "fee_user")
LYSHOP_HOST_URL = os.getenv('LYSHOP_HOST_URL')
LYSHOP_RECHARGE_USER = os.getenv('LYSHOP_RECHARGE_USER')
LYSHOP_PAY_REQUEST_URL = os.getenv('LYSHOP_PAY_REQUEST_URL')
CURRENCY = os.getenv('LYSHOP_CURRENCY') 

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'api.apps.ApiConfig',
    'dashboard.apps.DashboardConfig',
    'catalog.apps.CatalogConfig',
    'accounts',
    'cart.apps.CartConfig',
    'orders.apps.OrdersConfig',
    'shipment.apps.ShipmentConfig',
    'vendors.apps.VendorsConfig',
    'payment.apps.PaymentConfig',
    'addressbook.apps.AddressbookConfig',
    'core.apps.CoreConfig',
    'inventory.apps.InventoryConfig',
]

# RESTFRAMEWORK SETTINGS
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        #'rest_framework.permissions.IsAdminUser',
        #'rest_framework.permissions.IsAuthenticated',
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    
    'DEFAULT_AUTHENTICATION_CLASSES': [
        #'rest_framework.authentication.BasicAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ]
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'inventory.middleware.VisitorCounter',
    'inventory.middleware.UniqueIPCounter',
    
]

ROOT_URLCONF = 'lyshop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'lyshop.context_processors.site_context',
                'accounts.context_processors.account_context',
                'catalog.context_processors.catalog_context',
                'orders.context_processors.order_context',
                'dashboard.context_processors.dashboard_context',
                'vendors.context_processors.vendor_context',

            ],
        },
    },
]


WSGI_APPLICATION = 'lyshop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'dev': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'lyshop.db'),
    },
    'production': {
	'ENGINE':  os.environ.get('LYSHOP_DATABASE_ENGINE'),
	'NAME'	:  os.environ.get('LYSHOP_DATABASE_NAME'),
	'USER'	:  os.environ.get('LYSHOP_DATABASE_USERNAME'),
	'PASSWORD':  os.environ.get('LYSHOP_DATABASE_PW'),
	'HOST'	:  os.environ.get('LYSHOP_DATABASE_HOST') ,
	'PORT' 	:  os.environ.get('LYSHOP_DATABASE_PORT'),
    'OPTIONS' : {
        'sslmode': 'require'
    },
    'TEST'  :{
        'NAME': os.getenv('LYSHOP_TEST_DATABASE', 'test_db'),
    },
   },

}

DEFAULT_DATABASE = os.environ.get('DJANGO_DATABASE', 'dev')
DATABASES['default'] = DATABASES[DEFAULT_DATABASE]
DEV_MODE = DEFAULT_DATABASE == 'dev'
#CSRF_COOKIE_SECURE = not DEV_MODE


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEV_MODE
#DEBUG = True


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '{asctime} {levelname} {module} {message}',
            'style': '{',
        },
        'file': {
            'format': '{asctime} {levelname} {module} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename':'logs/lyshop.log'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        '' : {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        'django': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        }
    }
}

###############

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'fr'
LANGUAGES = (
    ('fr',_('French')),
    ('en',_('English')),
)
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]
TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DECIMAL_SEPAROTOR='.'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATICFILES_DIRS = [
    #BASE_DIR + "static",
    os.path.join(BASE_DIR, "static"),
]
