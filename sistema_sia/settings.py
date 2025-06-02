from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-5)_8fwz!g!e3v%yl8jei1fy$vmz_&k7x1&-gyyz96253u65+px")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")


# Aplicações instaladas
INSTALLED_APPS = [
    "daphne",  # Servidor ASGI
    "channels",  # Suporte WebSockets
    "rest_framework",  # Django REST Framework
    "rest_framework_simplejwt",  # JWT Authentication
    "ninja",  # Django Ninja
    'ninja_jwt',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'ninja_extra',
    'corsheaders',
    'apps.armazens',
    'apps.usuarios',
    'apps.robos',
    'apps.inventario',
    'apps.logs_erro',
    'apps.agendamentos',
    'apps.imagens',
    'apps.trajetorias',
]

# Configuração do ASGI
ASGI_APPLICATION = "sistema_sia.asgi.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'apps.usuarios.middleware.JWTAuthenticationMiddleware',
    'apps.usuarios.middleware.logging_middleware.ActionLoggingMiddleware'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{asctime} | {message}',
            'style': '{',
        },
    },
    'handlers': {
        'action_log_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/actions.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'simple',
        },
    },
    'loggers': {
        'action_logger': {
            'handlers': ['action_log_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
]


CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
]

# Configuração de URLs
ROOT_URLCONF = 'sistema_sia.urls'

# Configuração de templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

# WSGI Application
WSGI_APPLICATION = 'sistema_sia.wsgi.application'

# Banco de Dados
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("POSTGRES_DB", "sistema_sia"),
        'USER': os.getenv("POSTGRES_USER", "dev_user"),
        'PASSWORD': os.getenv("POSTGRES_PASSWORD", "9115An"),
        'HOST': os.getenv("POSTGRES_HOST", "localhost"),
        'PORT': os.getenv("POSTGRES_PORT", "5432"),
    }
}


# Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'ninja_jwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
# Garanta que está usando a mesma chave em todos os lugares
SIMPLE_JWT = {
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': '3qqWbEwBvZH7MWKWejsc7BIWL8ENFJsF-4h_vF2gxTAV2T06vzVYle5a6ZwBXbdVzr8',
    'VERIFYING_KEY': None,
}
# Configurações JWT customizadas
NINJA_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Configuração de autenticação padrão
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Modelo de usuário customizado
AUTH_USER_MODEL = 'usuarios.Usuario'

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]


