from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# Configurações básicas
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
    "apps.api_client"
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
    #'apps.usuarios.middleware.logging_middleware.ActionLoggingMiddleware'
]

# Configuração de logging
LOG_DIR = BASE_DIR / 'middleware'

if not LOG_DIR.exists():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Diretório de logs criado: {LOG_DIR}")

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
            'filename': LOG_DIR / 'actions.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'simple',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps.usuarios.middleware.logging_middleware': {
            'handlers': ['action_log_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# Configurações CORS
CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000'

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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("POSTGRES_DB", "neondb"),
        'USER': os.getenv("POSTGRES_USER", "neondb_owner"),
        'PASSWORD': os.getenv("POSTGRES_PASSWORD", "npg_n18ArKMGcyCx"),
        'HOST': os.getenv("POSTGRES_HOST", "ep-morning-fog-a8kvrvni.eastus2.azure.neon.tech"),
        'PORT': os.getenv("POSTGRES_PORT", "5432"),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}



# Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configurações do REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'ninja_jwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Configurações JWT
SIMPLE_JWT = {
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': '3qqWbEwBvZH7MWKWejsc7BIWL8ENFJsF-4h_vF2gxTAV2T06vzVYle5a6ZwBXbdVzr8',
    'VERIFYING_KEY': None,
}

NINJA_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Autenticação
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'usuarios.Usuario'

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]