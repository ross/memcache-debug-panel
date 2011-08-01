======================
Memcache Debug Toolbar
======================

The Memcache Debug Toolbar is an add-on for Django Debug Toolbar for tracking
memcached usage. It currently supports both the pylibmc and memcache libraries.

This is definitely beta software, but I've found it useful in work and personal
projects. Feedback welcome, patches appreciated. - Ross McFarland

Installation
============

#. Install and configure django-debug-toolbar

	https://github.com/robhudson/django-debug-toolbar

#. Add the `memcache_toolbar` app to your INSTALLED_APPS.

#. import the panel corresponding to the library you're using

   The following must be imported in your settings.py file so that it has a
   chance to replace the caching library with one capible of tracking. You'll
   probably want to import it in local_settings.py (if you use the pattern) or
   at least wrap the import line in if DEBUG:

   For memcache:

	import memcache_toolbar.panels.memcache

   For pylibmc:

	import memcache_toolbar.panels.pylibmc

Configuration
=============

#. Add the memcache or pylibmc panel to DEBUG_TOOLBAR_PANELS

   You'll need to add the panel corresponding to the library you'll be using to
   the list of debug toolbar's panels in the order in which you'd like it to
   appear.

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
