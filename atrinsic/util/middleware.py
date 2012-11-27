#!/usr/bin/python
from django.http import HttpResponseRedirect

from atrinsic.base.models import *
from copy import deepcopy

class OrganizationMiddleware(object):
    ''' Middleware that runs before views are processed to determine the authentication
        choice for this request'''

    def process_view(self,request,view_func,view_args,view_kwargs):
        if not request.user.is_authenticated():
            return None

        if request.META["PATH_INFO"].find("/accounts/choice/") == 0:
            return None
        if request.session.get("organization_id",None) == None and request.session.get("network_login",None) == None:
            return HttpResponseRedirect("/accounts/choice/")


        request.network_login = False
        if request.session.get("organization_id",None):
            try:
                request.organization = Organization.objects.get(id=request.session.get("organization_id"))
            except Organization.DoesNotExist:
                request.session["organization_id"] = None
                return None
                                                               
        if request.session.get("network_login",None):
            request.network_login = True
        return None


class WebRequestMiddleware(object):
    ''' Middleware that logs every WebRequest '''

    def process_response(self, request, response):
        if hasattr(request, 'session') and request.user.is_authenticated():
            u = request.user.email
        else:
            u = 'No User'

        if hasattr(request, 'organization'):
            o = request.organization
        else:
            o = 'No Organization'

        args = request.REQUEST.items()
        output = []
        for k,v in args:
            if k.find("password") != -1:
                output.append((k,"******************"))
            else:
                output.append((k,v))

        WebRequest.objects.create(method=request.method, url=request.META['PATH_INFO'], organization=o, 
                length=len(response.content), user=u, status=response.status_code,request=str(output))

        return response

class AdQuotientRedirect(object):
    def process_request(self, request):
        http_post = request.META.get('HTTP_HOST').lower()
        if http_post == 'dev.adquotient.com':
            return HttpResponseRedirect("http://network.dev.atrinsic.com")
        elif http_post == 'stg.adquotient.com':
            return HttpResponseRedirect("http://network.stg.atrinsic.com")
        elif http_post == 'www.adquotient.com':
            return HttpResponseRedirect("http://network.atrinsic.com")
        elif http_post == 'adquotient.com':
            return HttpResponseRedirect("http://network.atrinsic.com")
        return None