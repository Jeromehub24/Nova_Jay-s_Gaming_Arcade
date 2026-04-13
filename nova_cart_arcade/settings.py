"""
Settings for the Nova Cart Arcade project.

The app is configured for MariaDB during normal use and falls back to SQLite
for automated tests so the test suite stays self-contained.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_flag(name, default=False):
    """Return a boolean-style environment variable as ``True`` or ``False``."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-4jyi8icjmc6f@8!e-0zu7e$p3p^t6ghbk@hts%!g-!u*x(+0pb",
)
DEBUG = env_flag("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if host.strip()
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "storefront",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "nova_cart_arcade.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "storefront.context_processors.storefront_context",
            ],
        },
    },
]


WSGI_APPLICATION = "nova_cart_arcade.wsgi.application"


DB_ENGINE = os.getenv("NOVA_CART_DB_ENGINE", "mariadb").lower()
RUNNING_TESTS = "test" in sys.argv

# Default to MariaDB for app usage, but keep tests independent of a local DB.
if RUNNING_TESTS or DB_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("NOVA_CART_DB_NAME", "nova_cart_arcade"),
            "USER": os.getenv("NOVA_CART_DB_USER", "root"),
            "PASSWORD": os.getenv("NOVA_CART_DB_PASSWORD", ""),
            "HOST": os.getenv("NOVA_CART_DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("NOVA_CART_DB_PORT", "3306"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Chicago"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

LOGIN_URL = "storefront:login"
LOGIN_REDIRECT_URL = "storefront:dashboard"
LOGOUT_REDIRECT_URL = "storefront:home"

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@novacart.local")
SERVER_EMAIL = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_flag("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env_flag("EMAIL_USE_SSL", default=False)
PASSWORD_RESET_TIMEOUT = 60 * 60

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get(
    "TWITTER_ACCESS_TOKEN_SECRET",
    "",
)
TWITTER_ENABLED = os.environ.get("TWITTER_ENABLED", "0") == "1"
TWITTER_LOG_FILE = BASE_DIR / "tweet_events.log"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
