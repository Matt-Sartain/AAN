import os
import datetime
import time
from django.template import Library
from atrinsic.base.models import Currency

register = Library()

@register.filter
def forex(value, currency):
    return currency.convert_display(value)

forex.is_safe = True

