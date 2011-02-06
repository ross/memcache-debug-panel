from django.conf.urls.defaults import *

urlpatterns = patterns('django.views.generic.simple',
    url(r'^$', 'direct_to_template', {'template': 'index.html'}, 'index')
)

urlpatterns += patterns('',
    url(r'^pylibmc/', include('examples.demo_pylibmc.urls')),
)
