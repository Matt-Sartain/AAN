import re 

from django import template
register = template.Library()

@register.filter
def csv_commas_replace(string): 
    return string.replace(",","")