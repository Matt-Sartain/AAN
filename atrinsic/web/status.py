from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from atrinsic.util.imports import *


@url(r"^server_status/$", "status_server")
def status_server(request):
    ''' XML view of ServerApplicationReport '''

    applications = ServerApplication.objects.all().order_by('-last_run')


    r = render_to_response('status/server.xml', {
            'applications' : applications,
        }, context_instance=RequestContext(request))

    r._headers['content-type'] = ('Content-Type', 'text/xml; charset=utf-8')

    return r


