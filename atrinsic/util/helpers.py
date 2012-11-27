from atrinsic.util.imports import *
from atrinsic.base.models import ServerApplication, ServerApplicationReport
from django.conf import settings
import datetime
import re


def log_application_status(name, status=None, result=None, description=None, sla=None):
    from atrinsic.base.models import ServerApplication,ServerApplicationReport
    if sla and description:
        (app, created)  = ServerApplication.objects.get_or_create(name=name, defaults={
            'name' : name, 
            'description' : description,
            'sla' : sla,
            'last_run' : datetime.datetime.now(),
            })
    else:
        app = ServerApplication.objects.get(name=name)

    app.last_run = datetime.datetime.now()
    app.save()
    
    if result:
        return ServerApplicationReport.objects.create(application=app, status=status, result=result)
    return None
    
def build_nav_menu(request, patterns):
    data_list = []
    found_current = False

    for item in patterns:
        if not found_current:
            found_current = \
                (re.search(item['regexp'], request.path) is not None)
            item['is_current'] = found_current
        else:
            item['is_current'] = False
        data_list.append(item)

    return data_list


def import_func(module_path):
    if module_path is None:
        return None

    module_list = module_path.split('.')
    module_parent = '.'.join(module_list[:-1])
    module_name = module_list[-1]
    module = __import__(module_parent, fromlist=[module_name])
    return getattr(module, module_name, None)


def build_tab_list(request, patterns):
    module_path = None
    for item in patterns:
        if re.search(item['regexp'], request.path):
            module_path = item['module']
            break

    module_func = import_func(module_path)
    return module_func(request.user) if callable(module_func) else []

    