from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.core.cache import cache

def index(request, **kwargs):
    cache.get('key')
    cache.get('key2')
    try:
        cache.incr('hello')
    except:
        pass
    return render_to_response('demo/index.html')

@cache_page(60 * 15, key_prefix='demo')
def cached(request, **kwargs):
    return index(request, **kwargs)
