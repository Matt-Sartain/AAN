#!/usr/bin/python
from django.http import HttpResponseRedirect, Http404,HttpResponse
from django.template.loader import render_to_string

def do_register_api(request,api_context=None):  
    '''
    check the request, if it's api, set attributes in the object
    '''

    if request.GET.get('api',None) == "True" and request.GET.get('api-version',None) == "1.0" and request.GET.get('api-output',None) in ['json']:
        request.api = True
        request.api_version = "1.0"
        request.api_output = request.GET["api-output"]
        request.api_context = api_context


class register_api(object):
    ''' Class representing an api wrapper'''

    def __init__(self,api_context):
        self.api_context = api_context

    def __call__(self,f):
        def wrapped_f(request,*args,**kwargs):
            do_register_api(request,self.api_context)
            return f(request,*args,**kwargs)
        return wrapped_f

    


class APIMiddleware(object):
    ''' Middleware that logs every WebRequest '''

    def process_response(self, request, response):
        if hasattr(request,"api"):
            if isinstance(response,HttpResponseRedirect):
                return HttpResponse("OK")
        return response


from django.utils import simplejson
def AQ_render_to_response(request,template,context,*args, **kwargs):
    
    if hasattr(request,"api"):
        # return a differently rendered resposne here
        output = {}
        if context.has_key('form'):
            output = context['form'].as_dictionary()
            
        if request.api_output == "json":
            return HttpResponse(
                simplejson.dumps(output),
                content_type = 'application/javascript; charset=utf8'
                )
    
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    return HttpResponse(render_to_string(template,context,*args, **kwargs), **httpresponse_kwargs)
        
