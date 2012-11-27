from django.conf.urls.defaults import *
import os

urlpatterns = patterns('aqanalytics.views.',
    (r'^get_report/(?P<report_name>.*)/$', 'get_report'),
    (r'^site_list/$', 'site_list'),
    (r'^login/$', 'login'),
    (r'^select_site/(?P<table_id>.*)/$', 'select_site'),
    (r'^reporting/$', 'reporting'),
    (r'^reporting/(?P<chart_type>.*)/(?P<start_date>.*)/(?P<end_date>.*)/$', 'get_flash_chart_data'),
   
)