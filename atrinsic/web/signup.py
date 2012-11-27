#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from atrinsic.util.imports import *

@url(r"^information/$","signup_advertiser_information")
def signup_advertiser(request):
    return AQ_render_to_response(request, 'signup/information.html', {}, context_instance=RequestContext(request))


@url(r"^advertiser/$","signup_advertiser")
def signup_advertiser(request):
    ''' View to handle the registration and signup for new Advertisers.  This view
        creates an AdvertiserApplication which can be used as a template for creating
        a new account by a Network Admin '''
    from forms import AdvertiserSignupForm,CaptchaForm
    from atrinsic.base.models import AdvertiserApplication
    if request.method == 'POST':
        form = AdvertiserSignupForm(request.POST)
        captcha_form = CaptchaForm(request.POST, initial={'captcha': request.META['REMOTE_ADDR']})

        if form.is_valid() and captcha_form.is_valid():
            if form.cleaned_data["country"] == "CA":
                form.cleaned_data["state"] = form.cleaned_data['province']
                
            del form.cleaned_data['province']
            adv = AdvertiserApplication.objects.create(**form.cleaned_data)
            
            from django.core.mail import EmailMultiAlternatives

            msg = EmailMultiAlternatives("Atrinsic Affiliate Network Advertiser Signup", """
Company Name: %s
Contact Name: %s %s
Email Address: %s
Website URL: %s

has submitted an application.
""" % (str(adv.organization_name),str(adv.contact_firstname[0:1].upper()+adv.contact_firstname[1:]),str(adv.contact_lastname[0:1].upper()+adv.contact_lastname[1:]), 
str(adv.contact_email),str(adv.website_url)),"admin@network.atrinsic.com", ["samantha.morris@atrinsic.com", "Aaron.Baker@atrinsic.com", "Kevin.Carney@atrinsic.com"])
            msg.send()

            # Send Advertiser Welcome Email
            msg = EmailMultiAlternatives("Thank you for  your interest in the Atrinsic Affiliate Network.", """
Prior to  launching as an advertiser, our sales team must evaluate your business' compatibility with our network. In order to do so, a member of the team will be in touch via email within the next 48 hours with some additional questions.

Please note that should your site not meet the basic criteria below, we will not be able to launch you on our affiliate network at this time.

    Site contains a secure shopping cart, a published return policy and guarantee, email communication confirming purchase and delivery of goods or services, and access to customer support
    Site contains no pop-ups on landing pages
    No template or blog sites
    Not a regional site that is only targeting a small market

How to know if you’re an Advertiser or Publisher?

    What is an advertiser?
    An advertiser, also known as a merchant or retailer, is a Web site or company that sells a product or service online, accepts payments and fulfills orders. Advertisers partner with publishers to help promote their products and services.<br /><br />
    What is a publisher?
    A publisher, also known as an affiliate or reseller, is an independent party  that promotes products and services of an advertiser in exchange for a  commission on leads or sales. A publisher displays an advertiser's ads, text  links, or product links on their Web site, in e-mail campaigns, or in search  listings. Signing up as a publisher is a free service.

If you have  completed the Advertiser sign-up form but are a better fit for a publisher  account, please contact client support at publisherapplication@network.atrinsic.com and we will assist in the transition  of your application.

Regards – 
The Atrinsic  Affiliate Network Team

*Atrinsic Interactive is a full-service interactive agency. We are not just a vertical search agency, ad network or affiliate network. We offer a cross-platform approach to deliver customers to you in the most cost-efficient manner possible. We bring together individual experts and sophisticated business tools to drive significant results for our advertisers.

**Atrinsic is an integrated media company. We drive growing audiences from our content network and third party distribution channels to acquire high value customers for advertisers and our own products. Atrinsic is now one of the top digital performance marketing companies in the United States, which also provides exceptional entertainment content that draws 25 million unique visitors per month.""","admin@network.atrinsic.com",[adv.contact_email])

            msg.attach_alternative("""
<p>Prior to  launching as an advertiser, our sales team must evaluate your business' compatibility with our network. In order to do so, a member of the team will be in touch via email within the next 48 hours with some additional questions.</p>
<p>Please note that should your site not meet the basic criteria below, we will not be able to launch you on our affiliate network at this time.</p>
<ul type="disc">
  <li>Site contains a secure shopping cart, a published return policy and guarantee, email communication confirming purchase and delivery of goods or services, and access to customer support</li>
  <li>Site contains no pop-ups on landing pages</li>
  <li>No template or blog sites</li>
  <li>Not a regional site that is only targeting a small market</li>
</ul>
<p>How to know if you’re an Advertiser or Publisher?<br /><br />
  What is an advertiser?<br />
  An advertiser, also known as a merchant or retailer, is a Web site or company that sells a product or service online, accepts payments and fulfills orders. Advertisers partner with publishers to help promote their products and services.<br /><br />
  What is a publisher?<br />
  A publisher, also known as an affiliate or reseller, is an independent party  that promotes products and services of an advertiser in exchange for a  commission on leads or sales. A publisher displays an advertiser's ads, text  links, or product links on their Web site, in e-mail campaigns, or in search  listings. Signing up as a publisher is a free service.<br /><br />
  If you have  completed the Advertiser sign-up form but are a better fit for a publisher  account, please contact client support at <a href="mailto:publisherapplication@network.atrinsic.com">publisherapplication@network.atrinsic.com</a> and we will assist in the transition  of your application.</p>
<p>Regards – <br />
  The Atrinsic  Affiliate Network Team</p>
<p>&nbsp;</p>
<p>*Atrinsic Interactive is a full-service interactive agency. We are not just a vertical search agency, ad network or affiliate network. We offer a cross-platform approach to deliver customers to you in the most cost-efficient manner possible. We bring together individual experts and sophisticated business tools to drive significant results for our advertisers.</p>
<p>**Atrinsic is an integrated media company. We drive growing audiences from our content network and third party distribution channels to acquire high value customers for advertisers and our own products. Atrinsic is now one of the top digital performance marketing companies<br />
  in the United States, which also provides exceptional entertainment content that draws 25 million unique visitors per month.</p>  
""", "text/html")
            msg.send()
            return AQ_render_to_response(request, 'signup/complete.html', { }, context_instance=RequestContext(request))
    else:
        form = AdvertiserSignupForm()
        captcha_form = CaptchaForm()

    return AQ_render_to_response(request, 'signup/advertiser.html', {
            'form' : form,
            'captcha_form' : captcha_form,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/step1/$","signup_advertiser_step1")
def signup_advertiser_step1(request):
    from forms import AdvertiserSignupForm1, AdvertiserSignupForm1_b
    from atrinsic.base.models import AdvertiserApplication
    from datetime import date
    
    adv = None
        
    if request.method == "POST":
        form = AdvertiserSignupForm1(request.POST)
        form_contact = AdvertiserSignupForm1_b(request.POST) 
        
        if form.is_valid() and form_contact.is_valid():            
            if form.cleaned_data["country"] == "CA":
                form.cleaned_data["state"] = form.cleaned_data['province']
                
            del form.cleaned_data['province']
                    
            adv = AdvertiserApplication.objects.create(                        
                contact_firstname = form_contact.cleaned_data['contact_firstname'],
                contact_lastname =  form_contact.cleaned_data['contact_lastname'],
                contact_email =     form_contact.cleaned_data['contact_email'],
                contact_phone =     form_contact.cleaned_data['contact_phone'],
                contact_fax =       form_contact.cleaned_data['contact_fax'],
                organization_name = form.cleaned_data['organization_name'],
                address =   form.cleaned_data['address'],
                address2 =  form.cleaned_data['address2'],
                city =      form.cleaned_data['city'],
                state =     form.cleaned_data['state'],
                #province =  form.cleaned_data['province'],
                zipcode =   form.cleaned_data['zipcode'],
                country =   form.cleaned_data['country'],
                date_site_launched = date.today()
            )
                        
            return HttpResponseRedirect("/signup/advertiser/step2/%s" % adv.id)
    else:
        form = AdvertiserSignupForm1()
        form_contact = AdvertiserSignupForm1_b() 
        
        
    return AQ_render_to_response(request, 'signup/advertiser_step1.html', {
            'adv' : adv,
            'form' : form,
            'form_contact' : form_contact,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/step2/(?P<advertiser_id>\d+)$","signup_advertiser_step2")
def signup_advertiser_step2(request, advertiser_id):
    from forms import AdvertiserSignupForm2, AdvertiserSignupForm2_b
    from atrinsic.base.models import AdvertiserApplication
    from datetime import datetime
    
    
    if advertiser_id:
        try:
            adv = get_object_or_404(AdvertiserApplication, id=advertiser_id)
        except:
            return AQ_render_to_response(request, 'base/custom_error.html', {
                    'errmsg' : SIGNUP_INVALID_LINK,
                }, context_instance=RequestContext(request))
    #if advertiser_id != None:
    #adv = AdvertiserApplication.objects.get(id=advertiser_id)  
    
    if request.method == "POST":
        form = AdvertiserSignupForm2(request.POST)
        form_email = AdvertiserSignupForm2_b(request.POST)
        if form.is_valid() and form_email.is_valid():            
            adv.date_site_launched =    form.cleaned_data['date_site_launched']
            adv.website_url =           form.cleaned_data['website_url']
            adv.products_on_site =      form.cleaned_data['products_on_site']
            adv.technical_team_type =   form.cleaned_data['technical_team_type']
            adv.creative_team_type =    form.cleaned_data['creative_team_type']
            adv.has_existing_affiliate_program = form.cleaned_data['has_existing_affiliate_program']
            
            adv.participates_in_email =     form_email.cleaned_data['participates_in_email']
            adv.email_working_with_agency = form_email.cleaned_data['email_working_with_agency']
            adv.email_contact_desired =     form_email.cleaned_data['email_contact_desired']
            
            adv.save()
            return HttpResponseRedirect("/signup/advertiser/step3/%s" % adv.id)
    else:
        form = AdvertiserSignupForm2()
        form_email = AdvertiserSignupForm2_b()

    return AQ_render_to_response(request, 'signup/advertiser_step2.html', {
            'adv' : adv,
            'form' : form,
            'form_email' : form_email,
        }, context_instance=RequestContext(request))


@url(r"^advertiser/step3/(?P<advertiser_id>\d+)$","signup_advertiser_step3")
def signup_advertiser_step3(request, advertiser_id):
    from forms import AdvertiserSignupForm3, AdvertiserSignupForm3_b, CaptchaForm_b
    from atrinsic.base.models import AdvertiserApplication
    
    try:
        adv = AdvertiserApplication.objects.get(id=advertiser_id)
    except:
        return AQ_render_to_response(request, 'base/custom_error.html', {
                'errmsg' : SIGNUP_INVALID_LINK,
            }, context_instance=RequestContext(request))
                
    
    if request.method == "POST":
        form = AdvertiserSignupForm3(request.POST)
        form_seo = AdvertiserSignupForm3_b(request.POST)        
        form_captcha = CaptchaForm_b(request.POST, initial={'captcha': request.META['REMOTE_ADDR']})
        
        if form.is_valid() and form_seo.is_valid() and form_captcha.is_valid():
            adv.participates_in_ppc =     form.cleaned_data['participates_in_ppc']
            adv.ppc_working_with_agency = form.cleaned_data['ppc_working_with_agency']
            adv.ppc_contact_desired =     form.cleaned_data['ppc_contact_desired']
            
            adv.participates_in_seo =     form_seo.cleaned_data['participates_in_seo']
            adv.seo_working_with_agency = form_seo.cleaned_data['seo_working_with_agency']
            adv.seo_contact_desired =     form_seo.cleaned_data['seo_contact_desired']
        
            adv.save()
            
            from django.core.mail import EmailMultiAlternatives

            msg = EmailMultiAlternatives("Atrinsic Affiliate Network Advertiser Signup", """
Company Name: %s
Contact Name: %s %s
Email Address: %s
Website URL: %s

has submitted an application.
""" % (str(adv.organization_name),str(adv.contact_firstname[0:1].upper()+adv.contact_firstname[1:]),str(adv.contact_lastname[0:1].upper()+adv.contact_lastname[1:]), 
str(adv.contact_email),str(adv.website_url)),"admin@network.atrinsic.com", ["samantha.morris@atrinsic.com", "Aaron.Baker@atrinsic.com", "Kevin.Carney@atrinsic.com"])
            msg.send()

            # Send Advertiser Welcome Email
            msg = EmailMultiAlternatives("Thank you for  your interest in the Atrinsic Affiliate Network.", """
Prior to  launching as an advertiser, our sales team must evaluate your business' compatibility with our network. In order to do so, a member of the team will be in touch via email within the next 48 hours with some additional questions.

Please note that should your site not meet the basic criteria below, we will not be able to launch you on our affiliate network at this time.

    Site contains a secure shopping cart, a published return policy and guarantee, email communication confirming purchase and delivery of goods or services, and access to customer support
    Site contains no pop-ups on landing pages
    No template or blog sites
    Not a regional site that is only targeting a small market

How to know if you’re an Advertiser or Publisher?

    What is an advertiser?
    An advertiser, also known as a merchant or retailer, is a Web site or company that sells a product or service online, accepts payments and fulfills orders. Advertisers partner with publishers to help promote their products and services.<br /><br />
    What is a publisher?
    A publisher, also known as an affiliate or reseller, is an independent party  that promotes products and services of an advertiser in exchange for a  commission on leads or sales. A publisher displays an advertiser's ads, text  links, or product links on their Web site, in e-mail campaigns, or in search  listings. Signing up as a publisher is a free service.

If you have  completed the Advertiser sign-up form but are a better fit for a publisher  account, please contact client support at publisherapplication@network.atrinsic.com and we will assist in the transition  of your application.

Regards – 
The Atrinsic  Affiliate Network Team

*Atrinsic Interactive is a full-service interactive agency. We are not just a vertical search agency, ad network or affiliate network. We offer a cross-platform approach to deliver customers to you in the most cost-efficient manner possible. We bring together individual experts and sophisticated business tools to drive significant results for our advertisers.

**Atrinsic is an integrated media company. We drive growing audiences from our content network and third party distribution channels to acquire high value customers for advertisers and our own products. Atrinsic is now one of the top digital performance marketing companies in the United States, which also provides exceptional entertainment content that draws 25 million unique visitors per month.""","admin@network.atrinsic.com",[adv.contact_email])

            msg.attach_alternative("""
<p>Prior to  launching as an advertiser, our sales team must evaluate your business' compatibility with our network. In order to do so, a member of the team will be in touch via email within the next 48 hours with some additional questions.</p>
<p>Please note that should your site not meet the basic criteria below, we will not be able to launch you on our affiliate network at this time.</p>
<ul type="disc">
  <li>Site contains a secure shopping cart, a published return policy and guarantee, email communication confirming purchase and delivery of goods or services, and access to customer support</li>
  <li>Site contains no pop-ups on landing pages</li>
  <li>No template or blog sites</li>
  <li>Not a regional site that is only targeting a small market</li>
</ul>
<p>How to know if you’re an Advertiser or Publisher?<br /><br />
  What is an advertiser?<br />
  An advertiser, also known as a merchant or retailer, is a Web site or company that sells a product or service online, accepts payments and fulfills orders. Advertisers partner with publishers to help promote their products and services.<br /><br />
  What is a publisher?<br />
  A publisher, also known as an affiliate or reseller, is an independent party  that promotes products and services of an advertiser in exchange for a  commission on leads or sales. A publisher displays an advertiser's ads, text  links, or product links on their Web site, in e-mail campaigns, or in search  listings. Signing up as a publisher is a free service.<br /><br />
  If you have  completed the Advertiser sign-up form but are a better fit for a publisher  account, please contact client support at <a href="mailto:publisherapplication@network.atrinsic.com">publisherapplication@network.atrinsic.com</a> and we will assist in the transition  of your application.</p>
<p>Regards – <br />
  The Atrinsic  Affiliate Network Team</p>
<p>&nbsp;</p>
<p>*Atrinsic Interactive is a full-service interactive agency. We are not just a vertical search agency, ad network or affiliate network. We offer a cross-platform approach to deliver customers to you in the most cost-efficient manner possible. We bring together individual experts and sophisticated business tools to drive significant results for our advertisers.</p>
<p>**Atrinsic is an integrated media company. We drive growing audiences from our content network and third party distribution channels to acquire high value customers for advertisers and our own products. Atrinsic is now one of the top digital performance marketing companies<br />
  in the United States, which also provides exceptional entertainment content that draws 25 million unique visitors per month.</p>  
""", "text/html")
            msg.send()
            return AQ_render_to_response(request, 'signup/complete.html', { }, context_instance=RequestContext(request))            
    else:        
        form = AdvertiserSignupForm3()
        form_seo = AdvertiserSignupForm3_b()
        form_captcha = CaptchaForm_b(initial={'captcha': request.META['REMOTE_ADDR']})   
        
    return AQ_render_to_response(request, 'signup/advertiser_step3.html', {
            'adv' : adv,
            'form' : form,
            'form_seo' : form_seo,
            'form_captcha' : form_captcha,
        }, context_instance=RequestContext(request))


@url(r"^publisher/$","signup_publisher")
@url(r"^publisher/(?P<advertiser_id>\d+)/$","signup_publisher")
def signup_publisher(request, advertiser_id=None):
    ''' First step of publisher signup process'''
    from forms import PublisherSignupTofS
    from atrinsic.base.models import Organization,Terms_Accepted_Log,TermsCopy
    
    advertiser = None
    print advertiser_id
    if advertiser_id:
        advertiser = get_object_or_404(Organization, id=advertiser_id)
        print advertiser_id
	
    if request.session.get("accepted",None):    
        termsViewd = "1"
    else:
    	termsViewd = "0"
    	    
    if request.method == "POST":
        form = PublisherSignupTofS(request.POST)
        if form.is_valid():
            print "TERMS_"
            z = Terms_Accepted_Log(ip=request.META.get('REMOTE_ADDR','127.0.0.1'),term=TermsCopy.objects.get(pk=1))
            z.save()
            if not advertiser_id:
                return HttpResponseRedirect("/signup/publisher/step2/%s" % z.id)
            else:
                return HttpResponseRedirect("/signup/publisher/step2/%s/%s" % (advertiser_id,z.id))
        else:
            print "error"
    else:
        form = PublisherSignupTofS()
    
    return AQ_render_to_response(request, 'signup/publisher.html', {
            'advertiser' : advertiser,
            'form' : form,
            'termsViewd' : termsViewd,
        }, context_instance=RequestContext(request))


@url(r"^publisher/step2/(?P<term_id>\d+)$","signup_publisher_step2")
@url(r"^publisher/step2/(?P<advertiser_id>\d+)/(?P<term_id>\d+)/$","signup_publisher_step2")
def signup_publisher_step2(request, term_id,advertiser_id=None):
    ''' Second step of publisher signup process'''
    from forms import PublisherSignupForm2,CaptchaForm
    from atrinsic.base.models import Organization,Terms_Accepted_Log,PublisherApplication
    advertiser = None
    print "404"
    if advertiser_id:
        advertiser = get_object_or_404(Organization, id=advertiser_id)

    if request.method == "POST":
        form = PublisherSignupForm2(False,request.POST)
        captcha_form = CaptchaForm(request.POST, initial={'captcha': request.META['REMOTE_ADDR']})
        if form.is_valid() and captcha_form.is_valid():
            print "TERMS__"
            z = Terms_Accepted_Log.objects.get(pk=term_id)
            import random
            import string
            u  =PublisherApplication.objects.create(first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'],
                                                    email=form.cleaned_data['email'],validation_code="".join([random.choice(string.letters+string.digits) for x in range(10)]))
            
            u.set_password(form.cleaned_data['password'])

            u.save()
            z.organization_id=u.id
            z.save()
            request.session['pub_app']=u.id
            from django.core.mail import EmailMultiAlternatives
            link = settings.SECURE_HOST + "/signup/publisher/step4/?id=%s&key=%s" % (u.id,u.validation_code)

            msg = EmailMultiAlternatives("Atrinsic Affiliate Network Email Confirmation", """
Thank you for your interest in the Atrinsic Affiliate Network.

To start your application process, click on the link below.  Our secure application will then open in a new browser window.

Once you've completed the remainder of the application, our team will review your site and information submitted.  If your application is subject to approval, a member of our Publisher Team will perform a phone verification with you in the next 24-48 hours.

Please add us to your white list to ensure all of our communications are received.
Complete the sign-up process on our website: %s

Thank you for your interest and we look forward to working with you.
The Atrinsic Affiliate Network Team
""" % link,"admin@network.atrinsic.com",[u.email])

            msg.attach_alternative("""
Thank you for your interest in the Atrinsic Affiliate Network.<br/>
<br/>
To start your application process, click on the link below.  Our secure application will then open in a new browser window.<br/>
<br>
Once you've completed the remainder of the application, our team will review your site and information submitted.  If your application is subject to approval, a member of our Publisher Team will perform a phone verification with you in the next 24-48 hours.<br/>
<br/>
Please add us to your white list to ensure all of our communications are received.<br/>
Complete the sign-up process on our website <a href="%s">%s</a><br/>
<br/>
Thank you for your interest and we look forward to working with you.<br/>
The Atrinsic Affiliate Network Team<br/>"""% (link,link), "text/html")

            msg.send()

            if not advertiser_id:
                return HttpResponseRedirect("/signup/publisher/step3/")
            else:
                return HttpResponseRedirect("/signup/publisher/step3/%s/" % advertiser_id)
    else:
        form = PublisherSignupForm2()
        captcha_form = CaptchaForm()
    
    return AQ_render_to_response(request, 'signup/publisher_step2.html', {
            'advertiser' : advertiser,
            'form' : form,
            'captcha_form':captcha_form,
        }, context_instance=RequestContext(request))


@url(r"^publisher/step3/$","signup_publisher_step3")
@url(r"^publisher/step3/(?P<advertiser_id>\d+)/$","signup_publisher_step3")
def signup_publisher_step3(request, advertiser_id=None):
    ''' Third step of publisher signup process'''
    from atrinsic.base.models import Organization
    advertiser = None

    if advertiser_id:
        advertiser = get_object_or_404(Organization, id=advertiser_id)

    return AQ_render_to_response(request, 'signup/publisher_step3.html', {
            'advertiser' : advertiser,
        }, context_instance=RequestContext(request))



@url(r"^publisher/step4/$","signup_publisher_step4")
def signup_publisher_step4(request):
    ''' Fourth step of publisher signup process, confirms the email'''
    from forms import PublisherSignupForm3,WebsiteForm,PaymentInfoForm,ContactInfoForm, ContactInfoFormSmallest
    from atrinsic.util.user import generate_username
    from atrinsic.base.models import PublisherApplication,Organization,Website,OrganizationContacts,OrganizationPaymentInfo,User,UserProfile

    if request.method == "GET":
        if request.GET.get("id",None) and request.GET.get("key",None):
            if PublisherApplication.objects.filter(validation_code=request.GET['key'],id=request.GET['id']).count() > 0:
                app = PublisherApplication.objects.filter(validation_code=request.GET['key'],id=request.GET['id'])[0]
                form = PublisherSignupForm3(False)
                website_form = WebsiteForm()
                payment_form = PaymentInfoForm()   
                print app.email
                inits = { 'payeename':'', 
                          'firstname':'', 
                          'lastname':'', 
                          'phone':'', 
                          'email': app.email, }
                formCI = ContactInfoForm(initial=inits)
                inits = { 'xs_firstname':'', 
                          'xs_lastname':'', 
                          'xs_email': app.email, }
                formCIxs = ContactInfoFormSmallest(initial=inits)
                key = request.GET['key']
                appid = request.GET['id']
                
                return AQ_render_to_response(request, 'signup/publisher_newStep.html', {
                 'payment_form':payment_form,
                 'formCI' : formCI,
                 'formCIxs' : formCIxs,
                 'website_form':website_form,
                 'form' : form,
                 'key' : key,
                 'appid' : appid,
                    }, context_instance=RequestContext(request))
            else:
                #application could not be found
                return AQ_render_to_response(request, 'signup/appnotfound.html', {
                    }, context_instance=RequestContext(request))        
        else:
            return AQ_render_to_response(request, 'signup/publisher_step4.html', {
                    }, context_instance=RequestContext(request))        
    else:

        form = PublisherSignupForm3(False,request.POST)
        website_form = WebsiteForm(request.POST)
        payment_form = PaymentInfoForm(request.POST)
        formCI = ContactInfoForm(request.POST)
        formCIxs = ContactInfoFormSmallest(request.POST)
        key = request.POST['key']
        appid = request.POST['appid']
        
        if form.is_valid() and website_form.is_valid() and  payment_form.is_valid():
            useSmallContactForm = True
            if payment_form.cleaned_data['payment_method'] == PAYMENT_CHECK:
                if formCI.is_valid():
                    useSmallContactForm = False
                else:
                    #1 or more forms are not valid
                    return AQ_render_to_response(request, 'signup/publisher_newStep.html', {
                         'payment_form':payment_form,
                         'formCI' : formCI,
                         'formCIxs' : formCIxs,
                         'website_form':website_form,
                         'form' : form,
                         'key' : key,
                         'appid' : appid,
                            }, context_instance=RequestContext(request))
            else:
                if formCIxs.is_valid():
                    useSmallContactForm = True
                else:
                    #1 or more forms are not valid
                    return AQ_render_to_response(request, 'signup/publisher_newStep.html', {
                         'payment_form':payment_form,
                         'formCI' : formCI,
                         'formCIxs' : formCIxs,
                         'website_form':website_form,
                         'form' : form,
                         'key' : key,
                         'appid' : appid,
                            }, context_instance=RequestContext(request))
            #create Organization
           
            org = Organization.objects.create(org_type=ORGTYPE_PUBLISHER, status=ORGSTATUS_UNAPPROVED)

            org.company_name = form.cleaned_data['company_name']
            org.address = form.cleaned_data['pub_address']
            org.address2 = form.cleaned_data['pub_address2']
            org.city = form.cleaned_data['pub_city']
            org.state = form.cleaned_data['pub_state']
            org.zipcode = form.cleaned_data['pub_zipcode']
            org.country = form.cleaned_data['pub_country']
            if str(website_form.cleaned_data['vertical']) == "Adult":
                org.is_adult = 1
            org.save()
            
            if useSmallContactForm:     
                org_contact = OrganizationContacts.objects.create(organization=org, firstname=formCIxs.cleaned_data['xs_firstname'],lastname=formCIxs.cleaned_data['xs_lastname'],email=formCIxs.cleaned_data['xs_email'])
                org_contact.save()       
            else:        
                org_contact = OrganizationContacts.objects.create(organization=org, **formCI.cleaned_data)
                org_contact.save()
                address = formCI.cleaned_data['address']        
            app = PublisherApplication.objects.filter(validation_code=key,id=appid)[0]
            
            try:
                term_log = Terms_Accepted_Log.objects.get(organization_id=app)
                term_log.organization_id = org.id
                term_log.save()
            except:
                pass
            
            address = ""                
            website = Website.objects.create(publisher = org, is_default = True, **website_form.cleaned_data)
            website.save()
            org_payment = OrganizationPaymentInfo.objects.create(organization=org, **payment_form.cleaned_data)
            org_payment.save()
            
            first_name = app.first_name
            last_name = app.last_name
            password = app.password
            
            if useSmallContactForm:     
                email=formCIxs.cleaned_data['xs_email']
            else:      
                email=formCI.cleaned_data['email']
                            
            if payment_form.cleaned_data['payment_method'] == PAYMENT_CHECK:
                payee_name = formCI.cleaned_data['payeename']
                first_name = formCI.cleaned_data['firstname']
                last_name = formCI.cleaned_data['lastname']
            
            
            # Create User, Set Password, Map to Organization            
            u = User.objects.create(first_name=first_name,last_name=last_name,password=password,email=email, username=generate_username(email))
            up = UserProfile.objects.create(user=u)
            up.organizations.add(org)
            
            # Assign all ADMINLEVEL_ADMINISTRATOR to this
            for up in UserProfile.objects.filter(admin_level=ADMINLEVEL_ADMINISTRATOR):
                up.admin_assigned_organizations.add(org)
                up.save()
               
            #Emails
            from django.core.mail import EmailMultiAlternatives
            print "Sending mail"
            msg = EmailMultiAlternatives("Atrinsic Affiliate Network  Publisher Application", u"""
Dear """+first_name[0:1].upper()+first_name[1:]+""" """+last_name[0:1].upper()+last_name[1:]+""",

Thank you for applying to become a publisher on the Atrinsic Affiliate Network.

Your application has been placed in our queue and will be reviewed as quickly as possible.  You will be contacted shortly by a member of the Atrinsic Affiliate Network Publisher team to verify some information on your application.
If, at any time, you have questions or concerns, please contact us at publisherapplication@network.atrinsic.com.

We receive a large volume of applications each day and your application will be processed in the order in which it was received.


Thank you for your interest in working with Atrinsic Affiliate Network!

Sincerely,

The Atrinsic Affiliate Network Publisher Team

""","admin@network.atrinsic.com",[email])

            msg.send()
            
            themessage = u"""Dear Admin! this is a glorious day, a new publisher has join our ranks.
            Name: """+first_name[0:1].upper()+first_name[1:]+""" """+last_name[0:1].upper()+last_name[1:]
            themessage += """
            Address: """+address+"""
            Email: """+email+"""
            Website URL: """+website_form.cleaned_data['url']+"""
            
            please review this application,
            
            Sincerely,
            
            The Atrinsic Affiliate Network Robot that sends email"""
                
            msg2 = EmailMultiAlternatives("Atrinsic Affiliate Network Publisher Application",themessage,"admin@network.atrinsic.com",['publisherapplication@network.atrinsic.com'])
            msg2.send()    
                     
            return AQ_render_to_response(request, 'signup/publisher_complete.html', {
        }, context_instance=RequestContext(request))
        
        else:
            #1 or more forms are not valid
            return AQ_render_to_response(request, 'signup/publisher_newStep.html', {
                 'payment_form':payment_form,
                 'formCI' : formCI,
                 'formCIxs' : formCIxs,
                 'website_form':website_form,
                 'form' : form,
                 'key' : key,
                 'appid' : appid,
                    }, context_instance=RequestContext(request))
                    

@url(r"^publisher/complete/$","signup_publisher_complete")
def signup_publisher_complete(request):
    ''' Last step of the publisher signup process, shows some copy'''
    
    return AQ_render_to_response(request, 'signup/publisher_complete.html', {
        }, context_instance=RequestContext(request))
    



