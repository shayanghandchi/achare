# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB", "migrate_db"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT"),
        "CONN_MAX_AGE": int(os.environ.get("CONN_MAX_AGE", "0")),
        "CONN_HEALTH_CHECKS": os.environ.get("CONN_HEALTH_CHECKS", False) == "True",
    },
}

# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
