#!/usr/bin/python
from django.conf import settings

def db_context(request):
    data = {}

    if settings.DB_DEBUG:
        from django.db import connection
        data["queries"] = connection.queries[:]
    
    return data
