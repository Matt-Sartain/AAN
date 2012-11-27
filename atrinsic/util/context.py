from django.conf import settings
from django.core.urlresolvers import reverse

from atrinsic.base.models import *

def general_context(request):
    ''' The general Context used across the site '''

    data = {}
    if not request.user.is_authenticated():
        return data

    data["organization_options"] = request.user.get_profile().organizations.all()
    
    if request.session.get("organization_id",None):
        data["organization"] = Organization.objects.get(id=request.session["organization_id"])
        
    return data
