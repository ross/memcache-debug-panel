from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
import memcache
#import pylibmc

def index(request, **kwargs):
    client = memcache.Client(['127.0.0.1:11211'], debug=False)
    #client = pylibmc.Client(['127.0.0.1'], binary=True)
    client.get('key')
    client.get('key2')
    try:
        client.incr('hello')
    except:
        pass
    return render_to_response('demo/index.html')

@cache_page(60 * 15, key_prefix='demo')
def cached(request, **kwargs):
    return index(request, **kwargs)
