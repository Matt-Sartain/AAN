import os
import zipfile
from django.conf import settings
from django.core.files.base import ContentFile
from atrinsic.base.models import *

import random

def build_creatives(org, filename):
    try:
        zip = zipfile.ZipFile(filename, 'r')
    except IOError:
        return []

    if not zip:
        return []
    
    output = []
    for name in zip.namelist():
        img_data = zip.read(name)
        f = ContentFile(img_data)
        basename = os.path.basename(name)
        try:
            ext = os.path.splitext(basename)[1]
            ext = ext.lower()
            if ext in ('.jpg', '.jpeg', '.gif', '.png'):
                ai = AdvertiserImage(advertiser=org)
                ai.image.save("%s_%s%s" % (ai.advertiser.id,random.randint(0,1000),ext.lower()), f)
                ai.original_filename = basename
                ai.save()
                output.append(ai)
        except IndexError:
            pass

    zip.close()
    return output
