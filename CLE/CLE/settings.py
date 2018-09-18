"""
Django settings for CLE project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import getpass
import ipgetter

# Get public ip of server
PUBLIC_IP = ipgetter.myip()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR,"templates")
STATIC_DIR = os.path.join(BASE_DIR,"static")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '--2$vfi4$(vsdvf_@_(6x%$9^(-ea3h0gkr6p*8j)zf7!_y&je'
AES_SECRET_KEY = 'A$4Hj8dhf3c@aj87'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [PUBLIC_IP,'172.31.25.38',"cle-alb-433525205.ap-southeast-1.elb.amazonaws.com","localhost","127.0.0.1","52.76.46.177.xip.io"]

ADMIN_LOGIN = 'admin'
ADMIN_PASSWORD = 'admin'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Module_TeamManagement',
    'Module_Account',
    'Module_DeploymentMonitoring',
    'django.contrib.sites', # new
    'allauth', # new
    'allauth.account', # new
    'allauth.socialaccount', # new
    'allauth.socialaccount.providers.google', # new
    'django_celery_beat', # new
    'formtools',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CLE.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CLE.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

password = ''

if 'posix' in os.name and 'alfaried' in getpass.getuser():
    password = 'mysqldb12345'
elif 'posix' in os.name and 'ec2-user' in getpass.getuser():
    password = 'cle12345'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'App_Data',
        'USER': 'root',
        'PASSWORD': password,
        'HOST': 'localhost',
        'PORT': '3306',
    },
    'CLE_Data': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'CLE_Data',
        'USER': 'root',
        'PASSWORD': password,
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

DATABASE_ROUTERS = ['CLE.router.TMRouter']

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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


#social authentications

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SOCIALACCOUNT_ADAPTER = 'Module_Account.adapters.SocialAccountWhitelist'



SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'hd': 'smu.edu.sg'
        }
    }
}

SITE_ID = 2 # Check your Database to see site id

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = '/'



# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    STATIC_DIR,
    '/Thunderhead Monkeys/CLE/static',
]


FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

from celery.schedules import crontab
# If you need to execute every n day

# CELERY STUFF
# Celery application definition
# http://docs.celeryproject.org/en/v4.0.2/userguide/configuration.html
CELERY_BROKER_URL  = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Makassar'
CELERY_BEAT_SCHEDULE = {
    'task-number-one': { #name of scheduler
    'task': 'trailheadscrapper', #name of task
    'schedule':  100.0 #period of running in seconds
    #'arg's :  #if have args
    }
}
