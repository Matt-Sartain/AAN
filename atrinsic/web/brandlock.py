from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from atrinsic.util.imports import *

@url(r"^$", "brandlock")
def brandlock(request):
 


    return AQ_render_to_response(request, 'brandlock/brandlock_frame.html', {}, context_instance=RequestContext(request))
