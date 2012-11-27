import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
import django.core.handlers.wsgi
os.environ['DJANGO_SETTINGS_MODULE'] = 'atrinsic.settings'
application = django.core.handlers.wsgi.WSGIHandler()
