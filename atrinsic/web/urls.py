from django.conf.urls.defaults import *
import os

urlpatterns = patterns('',
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s\\htdocs\\css\\' % os.sys.path[0]}),
	(r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s\\htdocs\\images\\' % os.sys.path[0]}),
	(r'^adbuilder/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s\\htdocs\\adbuilder\\' % os.sys.path[0]}),
	(r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s\\htdocs\\js\\' % os.sys.path[0]}),
	(r'^ofc/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s\\htdocs\\ofc\\' % os.sys.path[0]}),
	(r'^pdf/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s\\htdocs\\pdf\\' % os.sys.path[0]}),

	#(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'c:/django/Adquotient/atrinsic/htdocs/css/'}),
	#(r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'c:/django/Adquotient/atrinsic/htdocs/images/'}),
	#(r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'c:/django/Adquotient/atrinsic/htdocs/js/'}),
	#(r'^ofc/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'c:/django/Adquotient/atrinsic/htdocs/ofc/'}),
	#(r'^pdf/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'c:/django/Adquotient/atrinsic/htdocs/pdf/'}),
	
	(r'^accounts/', include('atrinsic.web.auth')),
	(r'^advertiser/', include('atrinsic.web.advertiser')),
	(r'^advertiser/', include('atrinsic.web.advertiser_links')),
	(r'^advertiser/', include('atrinsic.web.advertiser_settings')),
	(r'^advertiser/', include('atrinsic.web.advertiser_messages')),
	(r'^advertiser/', include('atrinsic.web.advertiser_reports')),
	(r'^advertiser/', include('atrinsic.web.advertiser_brandlock')),
	#(r'^advertiser/', include('aqanalytics.views')),
	(r'^advertiser/', include('atrinsic.web.advertiser_analytics')),
	
	(r'^', include('atrinsic.web.misc')),
	(r'^publisher/', include('atrinsic.web.publisher')),
	(r'^publisher/', include('atrinsic.web.publisher_dashboard')),
	(r'^publisher/', include('atrinsic.web.publisher_links')),
	(r'^publisher/', include('atrinsic.web.publisher_messages')),
	(r'^publisher/', include('atrinsic.web.publisher_settings')),
	(r'^publisher/', include('atrinsic.web.publisher_reports')),
	(r'^publisher/', include('atrinsic.web.publisher_analytics')),
	
	(r'^signup/', include('atrinsic.web.signup')),
	(r'^network/', include('atrinsic.web.network_account')),
	(r'^network/', include('atrinsic.web.network_advertiser')),
	(r'^network/', include('atrinsic.web.network_admin')),
	(r'^network/', include('atrinsic.web.network_dashboard')),
	(r'^network/', include('atrinsic.web.network_publisher')),
	(r'^network/', include('atrinsic.web.network_manage_relationships')),
	(r'^network/', include('atrinsic.web.network_reports')),
	(r'^status/', include('atrinsic.web.status')),
	(r'^brandlock/', include('atrinsic.web.brandlock')),
	(r'^jessy/', include('atrinsic.web.jessy')),

	(r'^publishers/$', 'atrinsic.web.not_logged.publishers'),
	(r'^agencies/$', 'atrinsic.web.not_logged.agencies'),
	(r'^advertisers/$', 'atrinsic.web.not_logged.advertisers'),
	(r'^home/$', 'atrinsic.web.not_logged.home'),
	(r'^phl_test/$', 'atrinsic.web.not_logged.phil_test'),
	
	
	
)
