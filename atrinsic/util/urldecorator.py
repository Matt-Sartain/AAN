import sys

from django.core.urlresolvers import RegexURLResolver
from django.conf.urls.defaults import patterns,url as django_url

def url(*args):
        """
        Usage:
        @url(r'^users$')
        def get_user_list(request):
                ...

        @url(r'^info/$', r'^info/(.*)/$') # will match both
        @render_to('wiki.html')
        def wiki(request, title=''):
                ...
        """
        caller_filename = sys._getframe(1).f_code.co_filename
        module = None
        for m in sys.modules.values():
                if m and '__file__' in m.__dict__ and m.__file__.startswith(caller_filename):
                        module = m
                        break
        def _wrapper(f):
                if module:
                        if 'urlpatterns' not in module.__dict__:
                                module.urlpatterns = []
			url_pattern = args[0]
			if len(args) > 1:
				url_name = args[1]
				pattern = django_url(url_pattern,f,name=url_name)
			else:
				pattern = django_url(url_pattern,f)

			module.urlpatterns += patterns('',pattern)
                return f
        return _wrapper

def include_urlpatterns(regex, module):
        """
        Usage:

        # in top-level module code:
        urlpatterns = include_urlpatterns(r'^profile/', 'apps.myapp.views.profile')
        """
        return [RegexURLResolver(regex, module)]

