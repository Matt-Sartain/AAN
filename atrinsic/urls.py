from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^favicon.ico$','django.views.static.serve',{'path':'favicon.ico',
#                                                  'document_root':'/usr/local/web/atrinsic11/atrinsic/htdocs'}),
                                                  'document_root':'C:/AdQuotient/1.1/atrinsic/htdocs/'}),

    (r'^', include('atrinsic.web.urls')),

    (r'^admin/(.*)', admin.site.root),
#    (r'^xml', include('atrinsic.base.api')),
)
