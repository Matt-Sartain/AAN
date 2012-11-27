from django.db import models
from django import forms
from atrinsic.util.AceFieldLists import Ace
class salesPersonField(models.CharField):
    def __init__(self, *args, **kwargs):
        client = Ace()
        salesPersonList = client.getSalesPersonList()
        z=[]
        if salesPersonList != None:
            for x in salesPersonList:
                z.append((x.SalesPersonId, x.SalesPersonName))            
        kwargs.setdefault('choices', z)

        super(salesPersonField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

class FormsalesPersonField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
    	client = Ace()
        salesPersonList = client.getSalesPersonList()        
        z=[]
        if salesPersonList != None:
            for x in salesPersonList:
                z.append((x["SalesPersonId"], x["SalesPersonName"]))
        kwargs.setdefault('choices', z)
        super(FormsalesPersonField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "ChoiceField"