from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from atrinsic.base.choices import *

from urllib import quote

def user_passes_test(test_func, login_url=None):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    def _dec(view_func):
        def _checklogin(request, *args, **kwargs):
            login_url = reverse("auth_login")

            if test_func(request):
                if request.user.is_active:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect(login_url)

            return HttpResponseRedirect('%s?next=%s' % (login_url, quote(request.get_full_path())))

        _checklogin.__doc__ = view_func.__doc__
        _checklogin.__dict__ = view_func.__dict__

        return _checklogin
    return _dec

login_required = user_passes_test(lambda request: request.user.is_authenticated())
publisher_required = user_passes_test(lambda request: request.user.is_authenticated() and (hasattr(request,"organization") and request.organization.is_publisher()))
advertiser_required = user_passes_test(lambda request: request.user.is_authenticated() and hasattr(request,"organization") and request.organization.is_advertiser() and (request.organization.advertiser_account_type > 0 or request.user.get_profile().admin_level > 0))
limited_advertiser_required = user_passes_test(lambda request: request.user.is_authenticated() and request.organization.is_advertiser())
admin_required = user_passes_test(lambda request: request.user.is_authenticated() and request.user.get_profile().admin_level > 0)
superadmin_required = user_passes_test(lambda request: request.user.is_authenticated() and request.user.get_profile().admin_level == ADMINLEVEL_ADMINISTRATOR)
