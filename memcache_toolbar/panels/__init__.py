from datetime import datetime
from debug_toolbar.panels import DebugPanel
from django.template.loader import render_to_string
import logging

# TODO:
# - work thought various clients based on perf in
#   http://amix.dk/blog/post/19471

logger = logging.getLogger(__name__)

class Calls:
    def __init__(self):
        self.reset()

    def reset(self):
        self._calls = []

    def append(self, call):
        self._calls.append(call)

    def calls(self):
        return self._calls

    def size(self):
        return len(self._calls)

    def last(self):
        return self._calls[-1]

# NOTE this is not even close to thread-safe/aware
instance = Calls()

def record(func):
    def recorder(*args, **kwargs):
        call = {'function': func.__name__, 'args': None, 'exception': False}
        instance.append(call)
        # the try here is just being extra safe, it should not happen
        try:
            a = None
            # first arg is self, do we have another
            if len(args) > 1:
                a = args[1]
                # is it a dictionary (most likely multi)
                if isinstance(a, dict):
                    # just use it's keys
                    a = a.keys()
            # store the args
            call['args'] = a
        except e:
            logger.exception('tracking of call args failed')
        ret = None
        try:
            # the clock starts now
            call['start'] = datetime.now()
            ret = func(*args, **kwargs)
        except:
            call['exception'] = True
            raise
        finally:
            # the clock stops now
            dur = datetime.now() - call['start']
            call['duration'] = (dur.seconds * 1000) + (dur.microseconds / 1000.0)
        return ret
    return recorder

try:
    import pylibmc
    import _pylibmc

    # duplicating the client code sucks so hard, but it's necessary since the
    # original uses super and we'd need to inherit from it and then replace it
    # resulting in a class that inherits from itself :( see
    # http://fuhm.net/super-harmful/ anyway, see the bottom of this class for
    # the methods we're installing tracking on
    class TrackingClient(_pylibmc.client):
        def __init__(self, servers, binary=False):
            """Initialize a memcached client instance.

            This connects to the servers in *servers*, which will default to being
            TCP servers. If it looks like a filesystem path, a UNIX socket. If
            prefixed with `udp:`, a UDP connection.

            If *binary* is True, the binary memcached protocol is used.
            """
            self.binary = binary
            self.addresses = list(servers)
            addr_tups = []
            for server in servers:
                addr = server
                port = 11211
                if server.startswith("udp:"):
                    stype = _pylibmc.server_type_udp
                    addr = addr[4:]
                    if ":" in server:
                        (addr, port) = addr.split(":", 1)
                        port = int(port)
                elif ":" in server:
                    stype = _pylibmc.server_type_tcp
                    (addr, port) = server.split(":", 1)
                    port = int(port)
                elif "/" in server:
                    stype = _pylibmc.server_type_unix
                    port = 0
                else:
                    stype = _pylibmc.server_type_tcp
                addr_tups.append((stype, addr, port))
            _pylibmc.client.__init__(self, servers=addr_tups, binary=binary)

        def __repr__(self):
            return "%s(%r, binary=%r)" % (self.__class__.__name__,
                                          self.addresses, self.binary)

        def __str__(self):
            addrs = ", ".join(map(str, self.addresses))
            return "<%s for %s, binary=%r>" % (self.__class__.__name__,
                                               addrs, self.binary)

        def get_behaviors(self):
            """Gets the behaviors from the underlying C client instance.

            Reverses the integer constants for `hash` and `distribution` into more
            understandable string values. See *set_behaviors* for info.
            """
            bvrs = _pylibmc.client.get_behaviors(self)
            bvrs["hash"] = hashers_rvs[bvrs["hash"]]
            bvrs["distribution"] = distributions_rvs[bvrs["distribution"]]
            return BehaviorDict(self, bvrs)

        def set_behaviors(self, behaviors):
            """Sets the behaviors on the underlying C client instance.

            Takes care of morphing the `hash` key, if specified, into the
            corresponding integer constant (which the C client expects.) If,
            however, an unknown value is specified, it's passed on to the C client
            (where it most surely will error out.)

            This also happens for `distribution`.
            """
            behaviors = behaviors.copy()
            if behaviors.get("hash") is not None:
                behaviors["hash"] = hashers[behaviors["hash"]]
            if behaviors.get("ketama_hash") is not None:
                behaviors["ketama_hash"] = hashers[behaviors["ketama_hash"]]
            if behaviors.get("distribution") is not None:
                behaviors["distribution"] = distributions[behaviors["distribution"]]
            return _pylibmc.client.set_behaviors(self, behaviors)

        behaviors = property(get_behaviors, set_behaviors)
        @property
        def behaviours(self):
            raise AttributeError("nobody uses british spellings")

        # methods we're adding tracking to

        @record
        def get(self, *args, **kwargs):
            return _pylibmc.client.get(self, *args, **kwargs)

        @record
        def get_multi(self, *args, **kwargs):
            return _pylibmc.client.get_multi(self, *args, **kwargs)

        @record
        def set(self, *args, **kwargs):
            return _pylibmc.client.set(self, *args, **kwargs)

        @record
        def set_multi(self, *args, **kwargs):
            return _pylibmc.client.set_multi(self, *args, **kwargs)

        @record
        def add(self, *args, **kwargs):
            return _pylibmc.client.add(self, *args, **kwargs)

        @record
        def replace(self, *args, **kwargs):
            return _pylibmc.client.replace(self, *args, **kwargs)

        @record
        def append(self, *args, **kwargs):
            return _pylibmc.client.append(self, *args, **kwargs)

        @record
        def prepend(self, *args, **kwargs):
            return _pylibmc.client.prepend(self, *args, **kwargs)

        @record
        def incr(self, *args, **kwargs):
            return _pylibmc.client.incr(self, *args, **kwargs)

        @record
        def decr(self, *args, **kwargs):
            return _pylibmc.client.decr(self, *args, **kwargs)

        @record
        def delete(self, *args, **kwargs):
            return _pylibmc.client.delete(self, *args, **kwargs)

        # NOTE delete_multi is implemented by iterative over args calling delete
        # for each one. i could probably hide that here, but i actually think
        # it's best to show it since each one will be a seperate network
        # round-trip.
        @record
        def delete_multi(self, *args, **kwargs):
            return _pylibmc.client.delete_multi(self, *args, **kwargs)

        @record
        def flush_all(self, *args, **kwargs):
            return _pylibmc.client.flush_all(self, *args, **kwargs)

    # NOTE issubclass is true of both are the same class
    if not issubclass(pylibmc.Client, TrackingClient):
        logger.debug('installing pylibmc.Client with tracking')
        pylibmc.Client = TrackingClient

except:
    logger.debug('unable to install pylibmc.Client with tracking')

class MemcachePanel(DebugPanel):
    name = 'Memcache'
    has_content = True

    def process_request(self, request):
        instance.reset()

    def nav_title(self):
        return 'Memcache'

    def nav_subtitle(self):
        duration = 0
        calls = instance.calls()
        for call in calls:
            duration += call['duration']
        n = len(calls)
        if (n > 0):
            return "%d calls, %0.2fms" % (n, duration)
        else:
            return "0 calls"

    def title(self):
        return 'Memcache Calls'

    def url(self):
        return ''

    def content(self):
        duration = 0
        calls = instance.calls()
        for call in calls:
            duration += call['duration']

        context = self.context.copy()
        context.update({
            'calls': calls,
            'duration': duration,
        })

        return render_to_string('memcache_toolbar/panels/memcache.html',
                context)
