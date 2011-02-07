from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'demo.views.index', {}, 'index'),
    url(r'^cached$', 'demo.views.cached', {}, 'cached'),
)
