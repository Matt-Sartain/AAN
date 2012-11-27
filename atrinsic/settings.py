# Django settings for atrinsic project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DB_DEBUG = DEBUG

ADMINS = (
    ('Affiliate Network', 'affiliates-dev@atrinsic.com')
)

MANAGERS = ADMINS

import sys
import PIL.Image
sys.modules['Image'] = PIL.Image

SITE_CONTACT = 'admin@network.atrinsic.com'
SITE_URL = 'http://network.atrinsic.com' #must be change in local_settings.py, do a ticket for this

W9_PATH = 'http://www.irs.gov/pub/irs-pdf/fw9.pdf'
W9_UPLOAD_PATH = '/pdf/uploaded/'

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'adquotient_v11'
DATABASE_USER = 'adquotient'
DATABASE_PASSWORD = 'f7LqmfGqFo'
DATABASE_HOST = ''
DATABASE_PORT = ''
FTP_PORT='21'
FTP_SERVER='ftp.adquotient.com'
FTP_ADMIN_USER='FTPAccess'
FTP_ADMIN_PASSWORD='test'

DATE_FORMAT = 'm/d/Y'
JS_DATE_FORMAT = 'mm-dd-yy'
LABEL_DATE_FORMAT = 'MM-DD-YYYY'
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/var/www/vhosts/adquotient.com/adquotient/atrinsic/htdocs/images/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://network.dev.atrinsic.com/images/'


# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@n@0yj!w!yp^h9&2mh!h=wy@^7%hr#5*b)2uk5476-s75p6@*0'

# This must be changed to reflect LIVE ACE API within each servers local settings.
ACEAPI_URL = 'http://sos.corp.atrinsic.com/services/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'atrinsic.util.middleware.OrganizationMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'atrinsic.util.middleware.WebRequestMiddleware',
    'atrinsic.util.api.APIMiddleware',
)

ROOT_URLCONF = 'atrinsic.urls'

AUTHENTICATION_BACKENDS = ('atrinsic.util.backend.UserBackend',)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
        "django.core.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.request",
        'atrinsic.util.context.general_context',
        'atrinsic.util.tabs.tab_context',
        'atrinsic.util.right_side',
        'atrinsic.util.db_debug.db_context',
        
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'atrinsic.base',
    'atrinsic.web',
    'atrinsic.util',
    'pagination',
    'atrinsic.countries',
    
)

AUTH_PROFILE_MODULE = 'base.userprofile'



# change in production


RECAPTCHA_PUBLIC_KEY = '6LdxKQYAAAAAAMxlqQc-DXYwImKWvMKTz4KeRbBn'
RECAPTCHA_PRIVATE_KEY = '6LdxKQYAAAAAAIwij-fLaEaLe98-5sTxGoD_1StR'

INVITE_PARTNER_ID = 47
INVITE_MEDIA_USERNAME = "adquotient"
INVITE_MEDIA_PASSWORD = "t6FADrAb"
INVITE_MEDIA_HOST = "http://api-dashboard.invitemedia.com/"
INVITE_CLICK_TRACKER_HOST = "http://tracker.adquotient.com/"
INVITE_SECURE_CLICK_TRACKER_HOST = "https://tracker.adquotient.com/"
INVITE_PIXEL_TRACKER_HOST = "http://track.adquotient.com/"
INVITE_SECURE_PIXEL_TRACKER_HOST = "https://track.adquotient.com/"

ACE_COMPANYCONTACT_URL = "http://sos.dev.corp.atrinsic.com/services/CompanyExt.asmx/"
ACE_IO_URL = "http://sos.dev.corp.atrinsic.com/services/InsertionOrder.asmx/"
ACE_PO_URL = "http://sos.dev.corp.atrinsic.com/services/PurchaseOrder.asmx/"
ACE_DB_SERVER = "192.168.0.126"

#APE_CREATE = "http://admin.trk.dev.adquotient.com/a/"
APE_CREATE = "http://admin.trk.adquotient.com/a/"
APE_CREATE_DEV = "http://trk.dev.acetrk.com/a/"

# APE COMMISSION JUNCTION MAPPING:
APE_CJ_CREATE = "http://admin.trk.adquotient.com/a/cj/"
APE_CJ_CREATE_DEV = "http://trk.dev.acetrk.com/a/cj/"

APE_GET_URL = "http://trk.acetrk.com/a/"
APE_TRACKER_URL = "http://trk.acetrk.com/r/"
APE_PIXEL_URL = "http://trk.acetrk.com/t/"
APE_SECURE_PIXEL_URL = "https://trk.acetrk.com/t/"

#APE_USERNAME = 'adquotient'
#APE_PASSWORD = 'PrUt2ech'

APE_USERNAME = 'charles'
APE_PASSWORD = 'qwerty'

APE_IMG_PIXEL = 'aan_pixel.gif'
APE_IMPRESSION_TRACKING = "http://imps.acetrk.com/i/"

CDN_HOST = "http://cdn.network.atrinsic.com/user_images/" # this will be images.adquotient.com on production
CDN_HOST_URL = "http://cdn.network.atrinsic.com/" # this will be images.adquotient.com on production
FULL_HOST = "http://network.atrinsic.com"
SECURE_HOST = "https://network.atrinsic.com"

LOCALFTP_ROOT = "/mnt/nfs/adquotient/ftproot/"

KENSHOO_URL = "https://34.xg4ken.com/media/redir.php?track=1&token={{token}}&type=conv&val={{amt}}&orderId={{orderid}}&promoCode=&valueCurrency=USD"

HIDE_UNSYNCED_LINKS = True
from os.path import join, dirname, abspath
SITE_ROOT = dirname(abspath(__file__))

try:
    from local_settings import *
except ImportError:
    pass