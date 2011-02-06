# work around modules with the same name
from __future__ import absolute_import

from memcache_toolbar.panels import BasePanel, record
import logging

DEBUG = False

logger = logging.getLogger(__name__)
try:
    import memcache as memc

    origClient = None

    class TrackingMemcacheClient(memc.Client):

        @record
        def flush_all(self, *args, **kwargs):
            return origClient.flush_all(self, *args, **kwargs)

        @record
        def delete_multi(self, *args, **kwargs):
            return origClient.delete_multi(self, *args, **kwargs)

        @record
        def delete(self, *args, **kwargs):
            return origClient.delete(self, *args, **kwargs)

        @record
        def incr(self, *args, **kwargs):
            return origClient.incr(self, *args, **kwargs)

        @record
        def decr(self, *args, **kwargs):
            return origClient.decr(self, *args, **kwargs)

        @record
        def add(self, *args, **kwargs):
            return origClient.add(self, *args, **kwargs)

        @record
        def append(self, *args, **kwargs):
            return origClient.append(self, *args, **kwargs)

        @record
        def prepend(self, *args, **kwargs):
            return origClient.prepend(self, *args, **kwargs)

        @record
        def replace(self, *args, **kwargs):
            return origClient.replace(self, *args, **kwargs)

        @record
        def set(self, *args, **kwargs):
            return origClient.set(self, *args, **kwargs)

        @record
        def cas(self, *args, **kwargs):
            return origClient.cas(self, *args, **kwargs)

        @record
        def set_multi(self, *args, **kwargs):
            return origClient.set_multi(self, *args, **kwargs)

        @record
        def get(self, *args, **kwargs):
            return origClient.get(self, *args, **kwargs)

        @record
        def gets(self, *args, **kwargs):
            return origClient.gets(self, *args, **kwargs)

        @record
        def get_multi(self, *args, **kwargs):
            return origClient.get_multi(self, *args, **kwargs)

    # NOTE issubclass is true of both are the same class
    if not issubclass(memc.Client, TrackingMemcacheClient):
        logger.debug('installing memcache.Client with tracking')
        origClient = memc.Client
        memc.Client = TrackingMemcacheClient

except:
    if DEBUG:
        logger.exception('unable to install memcache.Client with tracking')
    else:
        logger.debug('unable to install memcache.Client with tracking')


class MemcachePanel(BasePanel):
    pass
