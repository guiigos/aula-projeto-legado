"""Configurações do backend Django do Sistema de Estacionamento."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# A API não usa sessões nem assinaturas; o valor padrão serve apenas para o Django iniciar.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'chave-de-desenvolvimento-nao-usar-em-producao')
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'api',
]

# Sem CsrfViewMiddleware: a API não usa autenticação por cookies.
MIDDLEWARE = [
    'estacionamento.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'estacionamento.urls'
WSGI_APPLICATION = 'estacionamento.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DB_PATH', BASE_DIR / 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Com DEBUG desligado o Django não mostra erros no console por padrão.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'django.request': {'handlers': ['console'], 'level': 'ERROR'}},
}
