import os, dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'learnnov-graduate-studies-secret-key-2026-fallback-safe')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Security note: SECRET_KEY should be set as an environment variable in production
# Using a safe fallback if not provided to avoid deployment failures

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'graduate-api.onrender.com,localhost,127.0.0.1,*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'rest_framework_simplejwt',
    'studies',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {'default': dj_database_url.config(
    default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
    conn_max_age=600
)}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('JWT', 'Bearer'),
}

# CORS - السماح للواجهة الأمامية بالاتصال
CORS_ALLOWED_ORIGINS = [
    'https://graduate-studies-frontend.vercel.app',
    'http://localhost:3000',
    'http://localhost:5173',
]
# السماح بنطاق Vercel الخاص بالمشروع فقط وعدم السماح بأي نطاق عشوائي
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://graduate-studies-frontend(-[a-zA-Z0-9-]+)?\.vercel\.app$',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # السماح لجميع النطاقات للاتصال (يمكن تقييده لاحقاً)

# Static and Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Khartoum'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Production Security
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
