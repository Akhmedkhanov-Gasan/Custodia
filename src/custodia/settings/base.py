import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = bool(int(os.getenv("DJANGO_DEBUG", "1")))
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    # Local apps
    "apps.core.apps.CoreConfig",
    "apps.authz.apps.AuthzConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.mock.apps.MockConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.accounts.middleware.JWTAuthMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "custodia.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "custodia.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Stockholm"
USE_I18N = USE_TZ = True

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.auth.DjangoUserAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Custodia API",
    "VERSION": "0.1.0",
}

JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_ACCESS_TTL_MIN = int(os.getenv("JWT_ACCESS_TTL_MIN", "15"))
JWT_REFRESH_TTL_DAYS = int(os.getenv("JWT_REFRESH_TTL_DAYS", "7"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps.accounts.middleware": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
}
