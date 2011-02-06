from django.shortcuts import render_to_response
import pylibmc

def index(request, **kwargs):
    client = pylibmc.Client(['127.0.0.1'], binary=True)
    client.get('key')
    client.get('key2')
    try:
        client.incr('hello')
    except:
        pass
    return render_to_response('demo_pylibmc/index.html')
