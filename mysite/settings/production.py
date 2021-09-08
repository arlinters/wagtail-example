from __future__ import absolute_import, unicode_literals
from .base import *
import os

DEBUG = False

try:
    from .local import *
except ImportError:
    pass
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']


env = os.environ.copy()
SECRET_KEY = env['SECRET_KEY']