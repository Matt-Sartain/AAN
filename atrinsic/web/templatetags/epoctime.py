import os
from django.template import Library
import datetime
import time

register = Library()

@register.filter
def epoctime(value):
    try:
        return time.mktime(datetime.datetime.strptime(value,"%Y/%m/%d").timetuple())
    except:
        return None
    
