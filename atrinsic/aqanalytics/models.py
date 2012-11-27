from django.db import models
import datetime

class Users(models.Model):
        
    from atrinsic.base.models import Organization    
        
    email = models.EmailField(blank=False, max_length=100)
    password = models.CharField(blank=False, max_length=16)
    date_joined = models.DateField(default=datetime.datetime.today)
    last_login = models.DateField(default=datetime.datetime.today)
    organization = models.ForeignKey(Organization)