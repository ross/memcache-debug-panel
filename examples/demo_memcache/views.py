from django.shortcuts import render_to_response
import memcache 

def index(request, **kwargs):
    client = memcache.Client(['127.0.0.1:11211'], debug=False)
    client.get('key')
    client.get('key2')
    try:
        client.incr('hello')
    except:
        pass
    return render_to_response('demo_memcache/index.html')
