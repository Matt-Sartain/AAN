#!/usr/bin/python

import re
tagpattern = re.compile(r'{(?P<tag>[^}]*)}',re.VERBOSE)
from atrinsic.base.models import *

class tagsub_class:
    ''' Class to handle the substitution and replacement of embedded tags within a buffer to be
        used in embedded content.  Tag substitution is based on the regular expression:
        
        {(P<tag>[^}]()},  for example: {subject}
    '''
    def __init__(self,advertiser,publisher,textonly):
        from django.template.defaultfilters import slugify
        
        
        self.textonly = textonly

    	self.subdict = {'first_name':'First Name _test'}
        
        if publisher != None and publisher.get_default_website():
            self.contact = OrganizationContacts.objects.get(organization=publisher)
            self.subdict['first_name'] = self.contact.firstname
            self.subdict['website_url'] = publisher.get_default_website().url
            for link in advertiser.link_set.all():
                getlink_url = settings.FULL_HOST + "/publisher/links/view/pub/%s/%s/%s/" % (link.id,publisher.id,publisher.generate_link_hash(link))
                if textonly:
                    getLink = "\r\nGet link: %s" % getlink_url
                else:
                    getLink = """  <a href="%s" target="new">Get Link</a>""" % getlink_url
                self.subdict['link_%s' % slugify(link.name).lower()] = link.track_html_ape(publisher.get_default_website()) + getLink
        else:
            website = Website.objects.all()[0]

            self.subdict['first_name'] = '{first_name}'
            self.subdict['website_url'] = website.url

            for link in advertiser.link_set.all():
                getlink_url = settings.FULL_HOST + "/publisher/links/view/%s/" % (link.id)
                
                if textonly:
                    getLink = "\r\nGet link: %s" % getlink_url
                else:
                    getLink = """  <a href="%s" target="new">Get Link</a>""" % getlink_url

                self.subdict['link_%s' % slugify(link.name).lower()] = link.track_html_ape(website, False, True) + getLink
                
    def tagsub(self,match):
        tagname =  match.group("tag")
        if self.subdict.has_key(tagname):
            return self.subdict[tagname]
        return tagname

def render_text(msg,advertiser,publisher):
    ''' Helper function that uses the tagsub class to render text '''
    return tagpattern.sub(tagsub_class(advertiser,publisher,True).tagsub,msg)


def render_html(msg,advertiser,publisher):
    ''' Helper function that uses the tagsub class to render HTML'''
    return tagpattern.sub(tagsub_class(advertiser,publisher,False).tagsub,msg)
    

