#!/usr/bin/python
from atrinsic.base.choices import *


def superadmin_tab(request,cur_tab):
    return request.user.is_authenticated() and request.user.get_profile().admin_level == ADMINLEVEL_ADMINISTRATOR

def advertiser_tab(request,cur_tab):
    return request.user.is_authenticated() and hasattr(request,"organization") and request.organization.is_advertiser() and (request.organization.advertiser_account_type != ADVERTISERTYPE_MANAGED or request.user.get_profile().admin_level > 0)
