# Django settings for examples project.

import sys
from os.path import dirname, join
import logging
logging.basicConfig(level=logging.DEBUG)

# add our parent directory to the path so that we can find memcache_toolbar
sys.path.append('../')

# in order to track django's caching we need to import the panels code now
# so that it can swap out the client with one that tracks usage.
import memcache_toolbar.panels.memcache
# if you're using pylibmc use the following instead
#import memcache_toolbar.panels.pylibmc

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'examples.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
SECRET_KEY = 'rfca2x2s3465+3+=-6m!(!f3%nvy^d@g0_ykgawt*%6exoe3ti'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'examples.urls'

TEMPLATE_DIRS = (
        join(dirname(__file__), 'templates')
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    # external app
    'debug_toolbar',
    'memcache_toolbar',
    # apps
    'demo',
)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    'memcache_toolbar.panels.memcache.MemcachePanel',
    # if you use pyibmc you'd include it's panel instead
    #'memcache_toolbar.panels.pylibmc.PylibmcPanel',
)

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True
}
