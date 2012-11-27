import os
from recaptcha.client import captcha
from django.forms.util import ErrorList
from django.contrib.localflavor.us.forms import *
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.utils.safestring import mark_safe
from django.utils import dateformat
import time
from atrinsic.util.imports import *
from atrinsic.util.smartforms import *
from django.forms import ModelForm

class QualityScoringSystemMetricForm(SmartForm):
    ''' Form to add a Metric to the Quality Scoring System '''
    from atrinsic.base.models import QualityScoringSystemMetric
    key = forms.CharField(label='Key')
    weight = forms.FloatField(label='Weight')

    def clean_key(self):
        key = self.cleaned_data.get('key', None)

        if QualityScoringSystemMetric.objects.filter(key=key).count() > 0:
            raise forms.ValidationError(u"This Key already exists!")
            
        return key


class ProgramCPMForm(SmartForm):
    ''' Form to add cpm/cpc to Program Term '''

    cpm = forms.FloatField()
    cpc = forms.FloatField()

class SKUListProgramTermActionForm(SmartForm):
    ''' Form to associate a SKUList with a ProgramTerm Action '''

    #programterm_action = 
    skulist = forms.ChoiceField(label='SKU Lists')
    is_fixed_commission = forms.BooleanField(label='Is Commission Fixed? <br/><font size="-2">(If unchecked will use a percent)</font>',required=False)
    commission = forms.FloatField(label='Amount')

    def __init__(self, organization, *args, **kwargs):
        from atrinsic.base.models import SKUList
        super(SKUListProgramTermActionForm, self).__init__(*args, **kwargs)
        self.fields['skulist'].choices = [(a.id, a.name) for a in SKUList.objects.filter(advertiser=organization)]
        


class SKUListItemForm(SmartForm):
    ''' Form to add a SKUList Item '''
    item = forms.CharField(label='SKUList Item')


class SKUListForm(SmartForm):
    ''' Form to create a SKUList '''

    name = forms.CharField(label='Name')
    skufile = forms.FileField(label='SKU File')

    def __init__(self, *args, **kwargs):
        editing = kwargs.get('editing', False)

        if kwargs.has_key('editing'):
            kwargs.pop('editing')

        super(SKUListForm, self).__init__(*args, **kwargs)

        if editing:
            self.fields['skufile'].required = False
    def clean_skufile(self):
        file_type = self.cleaned_data.get('skufile').content_type
        if not file_type.find("text") >= 0:
            raise forms.ValidationError("file uploaded must be a tab delimited '.txt' file.")
        return self.cleaned_data.get('skufile')

class FormattedTextInput(forms.widgets.TextInput):
    "Overrides TextInput to render formatted value."
    def render(self, name, value, attrs=None):
        formatted_value = None
        if value:
            formatted_value = self.format_value(value)
        return super(FormattedTextInput, self).render(name, formatted_value, attrs)
        

class DateFormattedTextInput(FormattedTextInput):
    "Renders formatted date."
    def __init__(self, format=None, attrs=None):
        super(DateFormattedTextInput, self).__init__(attrs)
        self.format = format or settings.DATE_FORMAT

    def format_value(self, value):
        if isinstance(value, datetime.date) or isinstance(value, datetime.datetime):
            return dateformat.format(value, self.format)
        else:
            return value


class PublisherComparisonForm(SmartForm):
    ''' Form that selects Publisher Peer to Peer Comparison '''
 
    comparison = forms.ChoiceField(label='Comparison', choices=PEERTOPEER_PUBLISHER_CHOICES)
    metric = forms.ChoiceField(label='Metric', choices=METRIC_CHOICES)
    period = forms.ChoiceField(label='Period', choices=PEERTOPEERPERIOD_CHOICES)

class AdvertiserComparisonForm(SmartForm):
    ''' Form that selects Advertiser Peer to Peer Comparison '''

    comparison = forms.ChoiceField(label='Comparison', choices=PEERTOPEER_ADVERTISER_CHOICES)
    metric = forms.ChoiceField(label='Metric', choices=METRIC_CHOICES)
    period = forms.ChoiceField(label='Period', choices=PEERTOPEERPERIOD_CHOICES)

class ExchangeRateForm(SmartForm):
    class Meta:
        layout = ( 
            Fieldset("Edit Currency", "name", "rate", ),
        )
    ''' Form to set Exchange Rates in Network '''
    from atrinsic.base.models import Currency
    #from_currency = forms.ModelChoiceField(label='From Currency', queryset=Currency.objects.order_by('name'))
    #to_currency = forms.ModelChoiceField(label='To Currency', queryset=Currency.objects.order_by('name'))
    
    #currency = forms.ChoiceField(label='Currenncy', choices=Currency)
    
    name = forms.CharField(label='Currency')
    rate = forms.FloatField(label='Rate')
    

class EventsForm(SmartForm):
    events_status = forms.ChoiceField(label='Event Status', choices=NEWSSTATUS_CHOICES)
    events_name = forms.CharField(label='Event Name')
    events_date = forms.DateField(label='Date (MM/DD/YYYY)', widget = DateFormattedTextInput, required=True)
    location = forms.CharField(label='Location')
    registration = forms.URLField(label='Registration')
    data = forms.CharField(label='Optional Information', widget=forms.Textarea, required=False)



class ReportFormatForm(SmartForm):
    target = forms.ChoiceField(label='Download As', choices=REPORTFORMAT_CHOICES)

            
class WebRequestForm(SmartForm):
    date_from = forms.DateField(label='From (MM/DD/YYYY)', widget = DateFormattedTextInput, required=False)
    date_to = forms.DateField(label='To (MM/DD/YYYY)', widget = DateFormattedTextInput, required=False)

class NewsForm(SmartForm):
    news_status = forms.ChoiceField(label='News Status', choices=NEWSSTATUS_CHOICES)
    viewed_by = forms.ChoiceField(label='Viewed By', choices=NEWS_VIEWED_BY_CHOICES)
    data = forms.CharField(label='News', widget=forms.Textarea)

class ReCaptcha(forms.Widget):
    input_type = None # Subclasses must define this.

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        html = u"<script>var RecaptchaOptions = {theme : '%s'};</script>" % (
            final_attrs.get('theme', 'white'))
        html += captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY)
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        return {
            'recaptcha_challenge_field': data.get('recaptcha_challenge_field', None),
            'recaptcha_response_field': data.get('recaptcha_response_field', None),
        }

# hack: Inherit from FileField so a hack in Django passes us the
# initial value for our field, which should be set to the IP
class ReCaptchaField(forms.FileField):
    widget = ReCaptcha
    default_error_messages = {
        'invalid-site-public-key': u"Invalid public key",
        'invalid-site-private-key': u"Invalid private key",
        'invalid-request-cookie': u"Invalid cookie",
        'incorrect-captcha-sol': u"Invalid entry, please try again.",
        'verify-params-incorrect': u"The parameters to verify were incorrect, make sure you are passing all the required parameters.",
        'invalid-referrer': u"Invalid referrer domain",
        'recaptcha-not-reachable': u"Could not contact reCAPTCHA server",
    }

    def clean(self, data, initial):
        if initial is None or initial == '':
            raise Exception("ReCaptchaField requires the client's IP be set to the initial value")
        ip = initial
        resp = captcha.submit(data.get("recaptcha_challenge_field", None),
                              data.get("recaptcha_response_field", None),
                              settings.RECAPTCHA_PRIVATE_KEY, ip)
        if not resp.is_valid:
            raise forms.ValidationError(self.default_error_messages.get(
                    resp.error_code, "Unknown error: %s" % (resp.error_code)))

class CaptchaForm(SmartForm):
    class Meta:
        layout = (
            Fieldset("User Verification", "captcha"),
        )

    captcha = ReCaptchaField()

class CaptchaForm_b(SmartForm):
    class Meta:
        layout = (
            Fieldset("", "captcha"),
        )

    captcha = ReCaptchaField()
    
class RecruitForm(SmartForm):
    class Meta:
        layout = ( 
            Fieldset("Recruit Publishers", "program_term", "effective_date", ),
        )
    
    program_term = forms.ChoiceField(label='Recruit to Program Term')
    effective_date = forms.DateField(label='Effective Date', widget = DateFormattedTextInput, required=True)
	
    def __init__(self, organization, *args, **kwargs):
        super(RecruitForm, self).__init__(*args, **kwargs)
        from atrinsic.base.models import ProgramTerm
        self.fields['program_term'].choices = [(pt.id, pt.name) for pt in ProgramTerm.objects.filter(advertiser=organization).filter(is_archived=False)]

class DashboardSettingsForm(SmartForm):
    class Meta:
        layout = (
        
            Fieldset("Dashboard Settings", "dashboard_variable1"),
        )

    #dashboard_group_data_by = forms.ChoiceField(label='Group Data By', choices=REPORTGROUPBY_CHOICES, required=False)
    #start_date = forms.DateField(label='Start Date', required=False, widget = DateFormattedTextInput)
    #end_date = forms.DateField(label='End Date', required=False, widget = DateFormattedTextInput)
    #dashboard_viewing_programtype = forms.ChoiceField(label='Viewing Settings', choices=DASHBOARDVIEWINGPROGRAMTYPE_CHOICES, required=False)
    #dashboard_viewing_vertical = forms.ModelChoiceField(label='Viewing Vertical', queryset=PublisherVertical.objects.order_by('name').filter(is_adult=request.organization.is_adult), required=False)
    dashboard_variable1 = forms.ChoiceField(label='Ticker Variable',choices=DASHBOARDMETRIC_CHOICES_PUBLISHER, required=False)
    #dashboard_variable2 = forms.ChoiceField(label='Variable Two', choices=DASHBOARDMETRIC_CHOICES_PUBLISHER, required=False)
    
class WidgetSettingsForm(SmartForm):
    class Meta:
        layout = ("start_date", "end_date", "group_data_by","variable1","variable2" )

    group_data_by = forms.ChoiceField(label='Group Data By', choices=REPORTGROUPBY_CHOICES, required=False)
    start_date = forms.DateField(label='Start Date', required=False, widget = DateFormattedTextInput)
    end_date = forms.DateField(label='End Date', required=False, widget = DateFormattedTextInput)
    variable1 = forms.ChoiceField(label='Variable One', choices=DASHBOARDMETRIC_CHOICES_PUBLISHER, required=False)
    variable2 = forms.ChoiceField(label='Variable Two', choices=DASHBOARDMETRIC_CHOICES_PUBLISHER, required=False)

class AdvertiserAssignContactForm(SmartForm):
    class Meta:
        layout = (
            Fieldset("Assign Network Contact", "contact"),
        )

    contact = forms.ChoiceField(label='Contact')

    def __init__(self, organization, *args, **kwargs):
        super(AdvertiserAssignContactForm, self).__init__(*args, **kwargs)
        self.fields['organization'] = [(i.user.id,i.user) for i in organization.assigned_admins.all()]

    
class PublisherAssignContactForm(SmartForm):
    class Meta:
        layout = (
            Fieldset("Assign Network Contact", "contact"),
        )

    contact = forms.ChoiceField(label='Contact')
    def __init__(self, organization, *args, **kwargs):
        super(PublisherAssignContactForm, self).__init__(*args, **kwargs)
        self.fields['contact'].choices = [(i.user.id,i.user) for i in organization.assigned_admins.all()]



class TickerForm(SmartForm):
    class Meta:
        layout = (
            Fieldset("Set Organization Ticker", "ticker", ),
        )

    ticker = forms.CharField(label='Ticker', max_length=255)

    def clean_ticker(self):
        from atrinsic.base.models import Organization
        ticker = self.cleaned_data.get('ticker', None)

        if Organization.objects.filter(ticker=ticker).count() > 0:
            raise forms.ValidationError(u"This Ticker already exists!")

        return ticker


class NetworkRatingForm(SmartForm):
    ''' Form for setting Publisher Scores '''
    fields = { }

    def __init__(self, *args, **kwargs):
        super(NetworkRatingForm, self).__init__(*args, **kwargs)
        from atrinsic.base.models import QualityScoringSystemMetric
        for m in QualityScoringSystemMetric.objects.all().order_by('key'):
            self.fields[m.key] = forms.FloatField(label='Metric: %s' % m.key, required=True)

        self.layout = self.fields.keys()




class ForceForm(SmartForm):
    class Meta:
        layout = (
            Fieldset("Update Force", "force", ),
        )

    force = forms.FloatField(label='New Force')


class NetworkAdvertiserEditForm(SmartModelForm):
    
    class Meta:
        from atrinsic.base.models import Organization
        model = Organization
        
        fields = ('show_alias', 'company_name', 'company_alias','date_joined','is_private', 'brandlock', 'brandlock_key', 'ticker','ticker_symbol', 'address', 'address2', 'vertical', 'city','country', 'state', 'province', 'zipcode', 'salesperson', 'currency'
        )

        layout = (
            Fieldset("Advertiser Information", "company_name",'date_joined','is_private', 'brandlock', 'brandlock_key', 'vertical', "ticker","ticker_symbol", "show_alias", "company_alias","address", "address2", "city", "country", "state", "province", "zipcode", "salesperson", "currency" ),
        )
    def __init__(self, *args, **kwargs):
        super(NetworkAdvertiserEditForm, self).__init__(*args, **kwargs)
        from atrinsic.base.models import Ace_SalesPeople
        from atrinsic.base.models import OrganizationCurrency
        from atrinsic.base.models import Currency
        self.fields['currency'] = forms.ChoiceField(label='Currency')
        self.fields['currency'].choices = [(c.order, c.name) for c in Currency.objects.filter()]
        #self.fields['currency'].selected = 
        self.fields['province'] = FormProvinceField(label='Province', required=False)
        self.fields['province'].label = 'Province'
        self.fields['salesperson'] = forms.ChoiceField(label='Sales Person')
        self.fields['salesperson'].choices = [(a.sales_person_id, a.sales_person_name) for a in Ace_SalesPeople.objects.filter()]
        
class NetworkAdvertiserContactEditForm(SmartModelForm):
    
    class Meta:
        from atrinsic.base.models import OrganizationContacts
        model = OrganizationContacts

        fields = ('firstname', 'lastname','email', 'phone', 'fax', 
        )

        layout = (
            Fieldset("Contact Information", "firstname", "lastname", "email",
                     "phone", "fax", ),
        )
        
class NetworkAdvertiserBillingEditForm(SmartModelForm):
    
    class Meta:
        from atrinsic.base.models import OrganizationPaymentInfo
        model = OrganizationPaymentInfo

        fields = ('tax_classification', 'tax_id', 'vat_number',)

        layout = (
            Fieldset("Billing Information", "tax_classification", "tax_id", "vat_number", ) ,          
        )
        
class NetworkAdvertiserSettingsEditForm(SmartModelForm):
    
    class Meta:
        from atrinsic.base.models import Organization
        model = Organization

        fields = ('network_rating', 'force', 'advertiser_account_type', 'publisher_approval','allowed_banner', 
                'allowed_text', 'allowed_keyword', 'allowed_flash', 'allowed_email_link', 'allowed_datafeed', 'allowed_rss',
                'allow_third_party_email_campaigns', 'allow_direct_linking_through_ppc', 'allow_trademark_bidding_through_ppc', 
        )

        layout = (
            Fieldset("Advertiser Settings", "advertiser_account_type", "publisher_approval",
                     "network_rating", "force", "allowed_banner", "allowed_text", "allowed_keyword",
                     "allowed_flash", "allowed_email_link", "allowed_datafeed","allowed_rss","allow_third_party_email_campaigns",
                     "allow_direct_linking_through_ppc","allow_trademark_bidding_through_ppc", ),
        )

class IOFeeSettings(SmartForm):
    '''
    IO Fee Settings Form
    '''
    class Meta:
        layout = (
            Fieldset("IO Fee Settings", "setup", "setupamt", "management", "managementamt", "launch", "launchamt",
                     "dfi", "dfiamt", "creative", "creativeamt", "recruitment", "recruitmentamt",),
        )    
    from atrinsic.util.salesperson import FormsalesPersonField
    
    setup = forms.BooleanField(label='Setup',required=False)
    setupamt = forms.CharField(max_length=256,label='', required=False)
    management = forms.BooleanField(label='Management',required=False)
    managementamt = forms.CharField(max_length=256,label='', required=False)
    launch = forms.BooleanField(label='Launch',required=False)
    launchamt = forms.CharField(max_length=256,label='', required=False)
    dfi = forms.BooleanField(label='Data Feed Integration',required=False)
    dfiamt = forms.CharField(max_length=256,label='', required=False)
    creative = forms.BooleanField(label='Creative Services',required=False)
    creativeamt = forms.CharField(max_length=256,label='', required=False)
    recruitment = forms.BooleanField(label='Recruitment',required=False)
    recruitmentamt = forms.CharField(max_length=256,label='', required=False)
    salespeople =  FormsalesPersonField(label='Sales Person')

class NetworkAdvertiserOrgIOEditForm(SmartModelForm):
    
    class Meta:
        from atrinsic.base.models import Organization_IO
        model = Organization_IO

        fields = ('transaction_fee_type', 'transaction_fee_amount', 
        )



class AdvertiserSignupForm1(SmartForm):
    class Meta:
        layout = (
            Fieldset("","organization_name", "address", "address2", "city", "country", "state", "province", "zipcode"),
        )
    
    organization_name = forms.CharField(label='Company Name')
    address = forms.CharField(label='Street Address')
    address2 = forms.CharField(label='Apt / Suite', required=False)
    city = forms.CharField(label='City')
    state =  FormStateField(label='State')
    province = FormProvinceField(label='Province', required=False)
    zipcode = forms.CharField(label='Zip')
    country = FormCountryField(label='Country', required=False, partial = True)

    
class AdvertiserSignupForm1_b(SmartForm):    
    class Meta:
        layout = (
            Fieldset("","contact_firstname", "contact_lastname", "contact_email", "contact_phone", "contact_fax"),
        )
    
    contact_firstname = forms.CharField(label='Contact First Name')
    contact_lastname = forms.CharField(label='Contact Last Name')
    contact_email = forms.EmailField(label='Email Address')
    contact_phone = forms.CharField(label='Phone Number')
    contact_fax = forms.CharField(label='Fax Number', required=False)
    
class AdvertiserSignupForm2(SmartForm):
    class Meta:
        layout = (
            Fieldset("", "date_site_launched","website_url", "products_on_site", "technical_team_type",
                    "creative_team_type", "has_existing_affiliate_program"),
        )
        
    date_site_launched = forms.DateField(label='Date Site Launched (MM/DD/YYYY)', widget = DateFormattedTextInput)
    website_url = forms.URLField(label='Web site URL')
    products_on_site = forms.IntegerField(label='Number of Products on your Website')

    technical_team_type = forms.ChoiceField(label='Is your technical team Inhouse or Outsourced?', choices=TEAM_CHOICES)
    creative_team_type = forms.ChoiceField(label='Is your creative team Inhouse or Outsourced?', choices=TEAM_CHOICES)

    has_existing_affiliate_program = forms.ChoiceField(label='Do you have an existing affiliate program?',
        choices=[('1', 'Yes'), ('0', 'No')])

        
    def clean_has_existing_affiliate_program(self):
        a = self.data.get('has_existing_affiliate_program', False)
        if not a or a == '0':
            return False
        return True

        
class AdvertiserSignupForm2_b(SmartForm):
    class Meta:
        layout = (
            Fieldset("", "participates_in_email", "email_working_with_agency", 
                    "email_contact_desired", ),
        )

    participates_in_email = forms.ChoiceField(label='Do you currently participate in Email Marketing?',
        choices=[('1', 'Yes'), ('0', 'No')])
    email_working_with_agency = forms.ChoiceField(label='If Yes, are you working with an<br> internal team or an Agency?', choices=AGENCY_CHOICES)
    email_contact_desired = forms.ChoiceField(label='Would You Like a Sales Person To Contact<br> You About Our Email Marketing Services?',
        choices=[('1', 'Yes'), ('0', 'No')])
        
    def clean_participates_in_email(self):
        a = self.data.get('participates_in_email', False)
        if not a or a == '0':
            return False
        return True

    def clean_email_contact_desired(self):
        a = self.data.get('email_contact_desired', False)
        if not a or a == '0':
            return False
        return True
        
class AdvertiserSignupForm3(SmartForm):
    class Meta:
        layout = (
            Fieldset("", "participates_in_ppc", "ppc_working_with_agency", "ppc_contact_desired", ),
            #Fieldset("Tax Classification","tax_classification", "tax_id")
        )

    participates_in_ppc = forms.ChoiceField(label='Do You Participate in PPC/SEM?',
        choices=[('1', 'Yes'), ('0', 'No')])
    ppc_working_with_agency = forms.ChoiceField(label='If Yes, are you working with an<br> internal team or an Agency?', choices=AGENCY_CHOICES)
    ppc_contact_desired = forms.ChoiceField(label='Would You Like a Sales Person To Contact<br> You About Our PPC Services?',
        choices=[('1', 'Yes'), ('0', 'No')])


    def clean_participates_in_ppc(self):
        a = self.data.get('participates_in_ppc', False)
        if not a or a == '0':
            return False
        return True

    def clean_ppc_contact_desired(self):
        a = self.data.get('ppc_contact_desired', False)
        if not a or a == '0':
            return False
        return True

        
class AdvertiserSignupForm3_b(SmartForm):
    class Meta:
        layout = (
            Fieldset("", "participates_in_seo", "seo_working_with_agency", "seo_contact_desired", ),
            #Fieldset("Tax Classification","tax_classification", "tax_id")
        )
        
    participates_in_seo = forms.ChoiceField(label='Do you currently participate in SEO?',
        choices=[('1', 'Yes'), ('0', 'No')])
    seo_working_with_agency = forms.ChoiceField(label='If Yes, are you working with an<br> internal team or an Agency?', choices=AGENCY_CHOICES)
    seo_contact_desired = forms.ChoiceField(label='Would You Like a Sales Person To Contact<br> You About Our SEO Services?',
        choices=[('1', 'Yes'), ('0', 'No')])
        
    def clean_participates_in_seo(self):
        a = self.data.get('participates_in_seo', False)
        if not a or a == '0':
            return False
        return True

    def clean_seo_contact_desired(self):
        a = self.data.get('seo_contact_desired', False)
        if not a or a == '0':
            return False
        return True

class AdvertiserSignupForm(SmartForm):
    class Meta:
        layout = (
            Fieldset("Advertiser Address", "organization_name", "address", "address2", "city", "country", "state", "province", "zipcode"),
            Fieldset("Contact Information", "contact_firstname", "contact_lastname", "contact_email", "contact_phone", "contact_fax"),
            Fieldset("Marketing Details", "date_site_launched","website_url", "products_on_site", "technical_team_type",
                    "creative_team_type", "has_existing_affiliate_program"),
            Fieldset("PPC Details", "participates_in_ppc", "ppc_working_with_agency", "ppc_contact_desired", ),
            Fieldset("SEO Details", "participates_in_seo", "seo_working_with_agency", "seo_contact_desired", ),
            Fieldset("Email Marketing Details", "participates_in_email", "email_working_with_agency", 
                    "email_contact_desired", ),
            Fieldset("Tax Classification","tax_classification", "tax_id")
        )

    organization_name = forms.CharField(label='Company Name')
    contact_firstname = forms.CharField(label='Contact First Name')
    contact_lastname = forms.CharField(label='Contact Last Name')
    contact_email = forms.EmailField(label='Email Address')
    contact_phone = forms.CharField(label='Phone Number')
    contact_fax = forms.CharField(label='Fax Number', required=False)

    address = forms.CharField(label='Address')
    address2 = forms.CharField(label='', required=False)
    city = forms.CharField(label='City')
    state =  FormStateField(label='State')
    province = FormProvinceField(label='Province', required=False)
    zipcode = forms.CharField(label='Zip')
    country = FormCountryField(label='Country', required=False, partial = True)

    tax_classification = forms.ChoiceField(label='Select One', choices=TAXTYPE_CHOICES)
    tax_id = forms.CharField(label="Tax ID", required=False)

    date_site_launched = forms.DateField(label='Date Site Launched (MM/DD/YYYY)', widget = DateFormattedTextInput)
    website_url = forms.URLField(label='Web site URL')
    products_on_site = forms.IntegerField(label='Number of Products on your Website')

    technical_team_type = forms.ChoiceField(label='Is your technical team Inhouse or Outsourced?', choices=TEAM_CHOICES)
    creative_team_type = forms.ChoiceField(label='Is your creative team Inhouse or Outsourced?', choices=TEAM_CHOICES)

    has_existing_affiliate_program = forms.BooleanField(label='Do you have an existing affiliate program?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))

    participates_in_ppc = forms.BooleanField(label='Do You Participate in PPC/SEM?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))
    ppc_working_with_agency = forms.ChoiceField(label='If Yes, are you working with an internal team or an Agency?', choices=AGENCY_CHOICES)
    ppc_contact_desired = forms.BooleanField(label='Would You Like a Sales Person To Contact You About Our PPC Services?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))

    participates_in_seo = forms.BooleanField(label='Do you currently participate in SEO?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))
    seo_working_with_agency = forms.ChoiceField(label='If Yes, are you working with an internal team or an Agency?', choices=AGENCY_CHOICES)
    seo_contact_desired = forms.BooleanField(label='Would You Like a Sales Person To Contact You About Our SEO Services?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))

    participates_in_email = forms.BooleanField(label='Do you currently participate in Email Marketing?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))
    email_working_with_agency = forms.ChoiceField(label='If Yes, are you working with an internal team or an Agency?', choices=AGENCY_CHOICES)
    email_contact_desired = forms.BooleanField(label='Would You Like a Sales Person To Contact You About Our Email Marketing Services?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))

    def clean_has_existing_affiliate_program(self):
        a = self.data.get('has_existing_affiliate_program', False)
        if not a or a == '0':
            return False
        return True

    def clean_participates_in_ppc(self):
        a = self.data.get('participates_in_ppc', False)
        if not a or a == '0':
            return False
        return True

    def clean_ppc_contact_desired(self):
        a = self.data.get('ppc_contact_desired', False)
        if not a or a == '0':
            return False
        return True

    def clean_participates_in_seo(self):
        a = self.data.get('participates_in_seo', False)
        if not a or a == '0':
            return False
        return True

    def clean_seo_contact_desired(self):
        a = self.data.get('seo_contact_desired', False)
        if not a or a == '0':
            return False
        return True

    def clean_participates_in_email(self):
        a = self.data.get('participates_in_email', False)
        if not a or a == '0':
            return False
        return True

    def clean_email_contact_desired(self):
        a = self.data.get('email_contact_desired', False)
        if not a or a == '0':
            return False
        return True


class PublisherSignupForm(SmartForm):
    class Meta:
        layout = ( 
            Fieldset("Terms of Service", "agree_to_terms"),
            Fieldset("Publisher Information", "company_name", "vertical", "promotion_method", "website_url", "website_desc"),
            Fieldset("Login Information", "first_name", "last_name", "email", "password", "password2"),
            Fieldset("Publisher Address", "address", "address2", "city", "state", "zipcode"),
            Fieldset("Contact Information", "contact_phone", "contact_fax"),
        )
    
    from atrinsic.base.models import PromotionMethod,PublisherVertical
    
    agree_to_terms = forms.BooleanField(label='I have read and accepted the Terms of Service',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))

    company_name = forms.CharField(label='Organization Name')

    promotion_method = forms.ModelChoiceField(queryset=PromotionMethod.objects.order_by('name'), label='Promotion Method')
    vertical = forms.ModelChoiceField(queryset=PublisherVertical.objects.order_by('name').filter(is_adult=0), label='Publisher Vertical')

    first_name = forms.CharField(label='First Name')
    last_name = forms.CharField(label='Last Name')
    email = forms.EmailField(label='Email Address')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    address = forms.CharField(label='Address')
    address2 = forms.CharField(label='', required=False)
    city = forms.CharField(label='City')
    state = FormStateField(label='State')
    country = FormCountryField(label='Country', required=False)
    zipcode = forms.CharField(label='Zipcode')

    contact_phone = forms.CharField(label='Phone Number')
    contact_fax = forms.CharField(label='Fax Number', required=False)

    website_url = forms.CharField(label='Web site URL')
    website_desc = forms.CharField(max_length=4096, label='Web site Description', widget=forms.Textarea)

    def clean_agree_to_terms(self):
        a = self.data.get('agree_to_terms', False)
        if not a or a == '0':
            raise forms.ValidationError(u'You must agree to the Terms of Service to continue')

        return True

    def clean_password2(self):
        p = self.cleaned_data.get('password', None)
        p2 = self.cleaned_data.get('password2', None)

        if p != p2:
            raise forms.ValidationError(u'Passwords do not match')

        return p2

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        from atrinsic.base.models import User
        if hasattr(self, 'user_id'):
            qs = User.objects.filter(email=email).exclude(id=getattr(self, 'user_id'))
        else:
            qs = User.objects.filter(email=email)

        if qs.count() > 0:
            raise forms.ValidationError(u'This E-Mail address already exists.')

        return email

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name', None)
        from atrinsic.base.models import Organization
        if Organization.objects.filter(company_name=company_name).count() > 0:
            raise forms.ValidationError(u'This Organization name already exists.')

        return company_name

class PublisherSignupTofS(SmartForm):
    class Meta:
        layout = ("agree_to_terms", "org_name")
        
    org_name = forms.CharField(label = 'Please enter your full name which will serve as your digital signature:')    
    #agree_to_terms = forms.BooleanField(label='', widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))
    agree_to_terms = forms.ChoiceField(label='', choices=[('1', 'Yes'), ('0', 'No')])

    def clean_agree_to_terms(self):
        a = self.data.get('agree_to_terms', False)
        if not a or a == '0':
            raise forms.ValidationError(u'You must agree to the Terms of Service to continue')

        return True
    def clean_org_name(self):
        a = self.data.get('org_name', False)
        if not a or a == '':
            raise forms.ValidationError(u'You must enter your name to continue')

        return True
    
class PublisherSignupForm1(SmartForm):
    class Meta:
        layout = ( 
            Fieldset("", "agree_to_terms", "org_name", "accepted"),
        )
    org_name = forms.CharField(label = 'Please review the <a href="/publisher/terms/" style="text-decoration: underline; color:#2e72bb;">Terms of Service</a> and enter your full name which will serve as your digital signature:')
    agree_to_terms = forms.BooleanField(label='I have read and accepted the Terms of Service',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))
    accepted = forms.BooleanField(widget=forms.HiddenInput(),required=True) 
    
    def clean_agree_to_terms(self):
        a = self.data.get('agree_to_terms', False)
        if not a or a == '0':
            raise forms.ValidationError(u'You must agree to the Terms of Service to continue')

        return True
    def clean_org_name(self):
        a = self.data.get('org_name', False)
        if not a or a == '':
            raise forms.ValidationError(u'You must enter your name to continue')

        return True
    def clean_accepted(self):
        a = self.data.get('accepted', False)
        if not a or a == '0':
            raise forms.ValidationError(u'You must read the Terms of Service to continue')
        return True
        
        
        
class PublisherSignupForm2(SmartForm):
    class Meta:
        layout = ( 
            Fieldset("Login Information", "first_name", "last_name", "email", "password", "password2"),
        )

    first_name = forms.CharField(label='* First Name')
    last_name = forms.CharField(label='* Last Name')
    email = forms.EmailField(label='* Email Address')
    password = forms.CharField(label='* Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='* Confirm Password', widget=forms.PasswordInput, required=True)
    username = forms.CharField(label='User Name', required=False)
    def __init__(self, update=False, *args, **kwargs):
        super(PublisherSignupForm2, self).__init__(*args, **kwargs)
        self.update = update
        
    def clean_password2(self):
        p = self.cleaned_data.get('password', None)
        p2 = self.cleaned_data.get('password2', None)

        if p != p2:
            if not self.update:
                raise forms.ValidationError(u'Passwords do not match')
            else:
                if len(p) != 0:
                    raise forms.ValidationError(u'Passwords do not match')

        return p2

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        from atrinsic.base.models import User
        if hasattr(self, 'user_id'):
            qs = User.objects.filter(email=email).exclude(id=getattr(self, 'user_id'))
        else:
            qs = User.objects.filter(email=email)
        if qs.count() > 0:
            if not self.update:
                raise forms.ValidationError(u'This E-Mail address already exists.')

        return email

    def clean_username(self):
        from atrinsic.util.user import generate_username
        user_name = self.cleaned_data.get('user_name', None)
        email_cleaned = self.cleaned_data.get('email',None)
        if email_cleaned:
            user_name = generate_username(email_cleaned)
        else:
            if not self.update:
                raise forms.ValidationError(u'Email is already in use!')
            
        return user_name


class PublisherSignupForm3(SmartForm):
    class Meta:
        layout = ( 
            Fieldset("Organization Information", "company_name", "pub_address", "pub_address2", "pub_city", "pub_country", "pub_state", "pub_province", "pub_zipcode"),
        )

    company_name = forms.CharField(label='Organization Name<br>(First and Last Name if Individual):')
    pub_address = forms.CharField(label='Address 1:')
    pub_address2 = forms.CharField(label='Address 2:', required=False)
    pub_city = forms.CharField(label='City')
    pub_state = FormStateField(label='State', required=False)
    pub_province = FormProvinceField(label='Province', required=False)
    pub_zipcode = forms.CharField(label='Zip/Postal code', required=True)
    pub_country = FormCountryField(label='Country', required=True, initial='US')
    
    def __init__(self, update=False, *args, **kwargs):
        super(PublisherSignupForm3, self).__init__(*args, **kwargs)
        self.update = update
         
    def clean(self):
        clean_data = self.cleaned_data
        if clean_data.get('pub_country', 'US') == 'CA':
            clean_data['pub_state'] = clean_data['pub_province']
            if not re.match('^[a-zA-Z]{1}[0-9]{1}[a-zA-Z]{1}(\-| |){1}[0-9]{1}[a-zA-Z]{1}[0-9]{1}$', clean_data.get('pub_zipcode','')):
                raise forms.ValidationError(u'You must enter a valid canadian postal code.')
        if clean_data.has_key('pub_province'):
            del clean_data['pub_province']
        return clean_data
        
    def clean_company_name(self):
        from atrinsic.base.models import Organization
        company_name = self.cleaned_data.get('company_name', None)
        if not self.update:
            if Organization.objects.filter(company_name=company_name).count() > 0:
                raise forms.ValidationError(u'This Organization name already exists.')

        return company_name

class NetworkAdvertiserContactForm(SmartForm):

    class Meta:
        layout = (
            Fieldset("Contact Information", "contact_firstname", "contact_lastname", "contact_email", 
                     "contact_phone", "contact_fax", ),
        )

    contact_firstname = forms.CharField(max_length=256, label='First Name')
    contact_lastname = forms.CharField(max_length=256, label='First Name')
    contact_email = forms.EmailField(label='E-mail')
    contact_phone = forms.CharField(max_length='256', label='Phone Number')
    contact_fax = forms.CharField(max_length='256', label='Fax Number', required=False)

class NetworkAdvertiserAssignForm(SmartForm):
    ''' Form to Associate Admions with Advertisers
    '''

    class Meta:
        layout = (
            Fieldset("Add Network Manager", "advertiser", ),
        )
    from atrinsic.base.models import Organization
    
    advertiser = forms.MultipleChoiceField(choices=[ (o.id, o.name) for o in Organization.objects.filter(org_type=ORGTYPE_ADVERTISER) ])

class NetworkPublisherAssignForm(SmartForm):
    ''' Form to Associate Admions with Publishers
    '''

    class Meta:
        layout = (
            Fieldset("Add Network Manager", "publisher", ),
        )
    from atrinsic.base.models import Organization
    publisher = forms.MultipleChoiceField(choices=[ (o.id, o.name) for o in Organization.objects.filter(org_type=ORGTYPE_PUBLISHER) ])


class NetworkManagementForm(SmartForm):
    ''' Form to associate managers
    '''

    class Meta:
        layout = (
            Fieldset("Add Network Manager", "user", ),
        )
    from atrinsic.base.models import User
    user = forms.ChoiceField(choices=[ (u.id, '%s %s %s' % (u.first_name, u.last_name, u.email, )) for u in User.objects.filter(userprofile__admin_level__gt=0) ])
    
class NetworkDataFeedForm(SmartForm):
    ''' Form to Add Network Data Feed
    '''

    class Meta:
        layout = (
            Fieldset("Add Data Feed", "name", "landing_page_url", "status", "datafeed_type", "datafeed_format", ),
            Fieldset("Login Information", "username", "password", "server", ),
        )

    name = forms.CharField(label='Action Name')
    landing_page_url = forms.CharField(label='Landing Page URL')
    status = forms.ChoiceField(label='Status', choices=STATUS_CHOICES)
    datafeed_type = forms.ChoiceField(label='Feed Type', choices=DATAFEEDTYPE_CHOICES)
    datafeed_format = forms.ChoiceField(label='Feed Format', choices=DATAFEEDFORMAT_CHOICES)

    username = forms.CharField(label='Username', required=False)
    password = forms.CharField(label='Password', required=False)
    server = forms.CharField(label='Server', required=False)
 
 
class NetworkActionForm(SmartForm):
    ''' Form to Add Network Tracking Action
    '''

    class Meta:
        layout = (
            Fieldset("Add Tracking Action", "name", "status","advertiser_payout_type","advertiser_payout_amount",
            "invite_id", "salespeople",),
        )
    from atrinsic.util.salesperson import FormsalesPersonField
    name = forms.CharField(label='Action Name')
    status = forms.ChoiceField(label='Status', choices=STATUS_CHOICES)
    
    advertiser_payout_type = forms.ChoiceField(label='Advertiser Payout Type',choices=ADVERTISER_PAYOUT_TYPE_CHOICES)
    advertiser_payout_amount = forms.FloatField(label='Advertiser Payout Amount')
        
    invite_id = forms.CharField(label='Tracking ID', required=False)
    salespeople =  FormsalesPersonField(label='Sales Person')
   
class NetworkViolationForm(SmartForm):
    ''' Class to update Keyword and Trademark Violations
    '''

    class Meta:
        layout = ( 
            Fieldset("Violation Status", "trademark_violation", "keyword_violation", ),
        )

    trademark_violation = forms.BooleanField(label='Trademark Violation?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))
    keyword_violation = forms.BooleanField(label='Keyword Violation',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]))

    def clean_trademark_violation(self):
        if self.data.get('trademark_violation', '0') == '1':
            return True
        else:
            return False

    def clean_keyword_violation(self):
        if self.data.get('keyword_violation', '0') == '1':
            return True
        else:
            return False

class NetworkStatusForm(SmartForm):
    ''' Form to Update Network Status
    '''

    class Meta:
        layout = (
            Fieldset("Advertiser Status", "status", "is_adult", ),
        )

    status = forms.ChoiceField(label='Update Status To', choices=ORGSTATUS_CHOICES)
    is_adult = forms.ChoiceField(label='Is Adult', choices=((0,'Not adult'),(1,'Adult only')))

class PubNetworkStatusForm(SmartForm):
    ''' Form to Update Network Status
    '''

    class Meta:
        layout = (
            Fieldset("Publisher Status", "status", "is_adult", ),
        )

    status = forms.ChoiceField(label='Update Status To', choices=PUBORGSTATUS_CHOICES)
    is_adult = forms.ChoiceField(label='Is Adult', choices=((0,'Not adult'),(1,'Adult only')))

class IncentiveStatusForm(SmartForm):
    ''' Form to Update Incentive Site Transfer Status
    '''

    class Meta:
        layout = (
            Fieldset("Incentive Site Transfer Status", "status", ),
        )

    status = forms.ChoiceField(label='Update Status To', choices=(
        (STATUS_TEST,'Test'),
        (STATUS_LIVE,'Live')
        ))

class ProgramForm(SmartForm):
    ''' Program Terms Form
    '''

    name = forms.CharField(label='Program Name')


class CommissionTierForm(SmartForm):
    ''' Commission Tiers Form
    '''

    class Meta:
        layout = (
            Fieldset("Incentive", "incentive_type", "threshold", ),
            Fieldset("Commission", "new_commission", "bonus", ),
        )

    incentive_type = forms.ChoiceField(label='Incentive Type', choices=INCENTIVETYPE_CHOICES)
    threshold = forms.FloatField(label='Threshold')
    new_commission = forms.FloatField(label='New Commission', required=False)
    bonus = forms.FloatField(label='Enter A Flat Fee Bonus', required=False)

 
    def clean_new_commission(self):
        val = self.cleaned_data.get('new_commission', None)

        if not val:
            return 0.0

        return val  
    
    def clean_bonus(self):
        val = self.cleaned_data.get('bonus', None)
    
        if not val:
            if not self.cleaned_data.get('new_commission', None):
                raise forms.ValidationError(u'Specify a Bonus or New Commission')

            return 0.0

        return val

    
class ProgramActionForm(SmartModelForm):
    class Meta:
        from atrinsic.base.models import ProgramTermAction
        model = ProgramTermAction
        

        fields = ('action', 'action_referral_period','is_fixed_commission', 'commission', )
        
        layout = (
            Fieldset("Program Actions", "action", "action_referral_period",), 
            Fieldset("Commission", "is_fixed_commission", "commission", ),
        )   

    
            
    def __init__(self, action_choices, *args, **kwargs):
        super(ProgramActionForm, self).__init__(*args, **kwargs)
        self.fields['action'].choices = action_choices

class ProgramTermSpecialActionForm(ModelForm):
    class Meta:        
        fields = ('special_action', 'program_term_id', 'organization_id',)
        layout = (
            Fieldset("Special Program Term", 'special_action',),      
        )

            
    special_action = forms.CharField(label='Special Terms and Conditions', widget=forms.Textarea)      
            
    
class UserForm(SmartForm):

    class Meta:
        layout =  ("first_name", "last_name", "email", "password", "password2" )

    first_name = forms.CharField(max_length=256, label='First Name')
    last_name = forms.CharField(max_length=256, label='Last Name')

    email = forms.EmailField(max_length=256, label='E-mail Address')

    password = forms.CharField(max_length=256, label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=256, label='Confirm Password', widget=forms.PasswordInput)

    def clean_password2(self):
        p = self.data.get('password', None)
        p2 = self.data.get('password2', None)

        if p != p2:
            raise forms.ValidationError(u'Passwords do not match')

        return p2

    def clean_email(self):
        from atrinsic.base.models import User
        email = self.cleaned_data.get('email', None)

        if hasattr(self, 'user_id'):
            qs = User.objects.filter(email=email).exclude(id=getattr(self, 'user_id'))
        else:
            qs = User.objects.filter(email=email)

        if qs.count() > 0:
            raise forms.ValidationError(u'This E-Mail address already exists.')

        return email

class UserEditForm(UserForm):
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = False
        self.fields['password2'].required = False
    

class NetworkUserForm(UserForm):
    class Meta:
        layout =  (
            Fieldset("User Information",  "first_name", "last_name", "email", "password", "password2", "admin_level", ),
        )

    admin_level = forms.ChoiceField(label='Admin Level', choices=ADMINLEVEL_CHOICES)

class NetworkUserEditForm(UserForm):
    class Meta:
        layout =  (
            Fieldset("User Information",  "first_name", "last_name", "email", "password", "password2", "admin_level", ),
        )

    admin_level = forms.ChoiceField(label='Admin Level', choices=ADMINLEVEL_CHOICES)

    def __init__(self, *args, **kwargs):
        super(NetworkUserEditForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = False
        self.fields['password2'].required = False

 
class AlertForm(SmartForm):
    ''' Alert Form
    '''
    class Meta:
        layout = (
            Fieldset("Notify Me", "alert_field", "up_or_down", 
                     "change", ),
            Fieldset("Over This Time Period", "time_period", ),
        )

    alert_field = forms.ChoiceField(label='', choices=METRIC_CHOICES,widget=forms.widgets.RadioSelect)
    up_or_down = forms.BooleanField(label='', widget=forms.widgets.RadioSelect(choices=[('1', 'Increase'), ('0', 'Decrease')])) 
    change = forms.FloatField(label='By this percentage (e.g. 50)')
    time_period = forms.ChoiceField(label='', choices=ALERTTIMEPERIOD_CHOICES,widget=forms.widgets.RadioSelect)

    def clean_up_or_down(self):
        if self.data.get('up_or_down', False) == '1':
            return True

        return False

class FeedForm(SmartForm):
    ''' Feed Form
    '''

    name = forms.CharField(label='Name')
    landing_page_url = forms.CharField(label='Landing Page URL')
    
    datafeed_type = forms.ChoiceField(label='Type', choices=DATAFEEDTYPE_CHOICES)
    datafeed_format = forms.ChoiceField(label='Format', choices=DATAFEEDFORMAT_CHOICES)
    
    username = forms.CharField(label='Username', required=False)
    password = forms.CharField(label='Password', required=False)
    server = forms.CharField(label='Server', required=False)

    def clean_username(self):
        type = int(self.cleaned_data['datafeed_type'])
        if type == DATAFEEDTYPE_FTPPULL:
            if 'username' not in self.cleaned_data or \
               not self.cleaned_data['username']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['username']

    def clean_password(self):
        type = int(self.cleaned_data['datafeed_type'])
        if type == DATAFEEDTYPE_FTPPULL:
            if 'password' not in self.cleaned_data or \
               not self.cleaned_data['password']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['password']

    def clean_server(self):
        type = int(self.cleaned_data['datafeed_type'])
        if type == DATAFEEDTYPE_FTPPULL:
            if 'server' not in self.cleaned_data or \
               not self.cleaned_data['server']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['server']


class PublisherFeedForm(SmartForm):
    ''' Feed Form
    '''
    from atrinsic.base.models import Organization, PublisherRelationship
    
    advertiser = forms.ModelChoiceField(label='Advertiser',queryset=Organization.objects.all())

    datafeed_type = forms.ChoiceField(label='Delivery Method', choices=PUB_DATAFEEDTYPE_CHOICES)
    datafeed_format = forms.ChoiceField(label='Format', choices=PUB_DATAFEEDFORMAT_CHOICES)
    def __init__(self, *args, **kwargs):
        from atrinsic.base.models import DataFeed, Organization, PublisherRelationship
        org = kwargs.pop('org')
        super(PublisherFeedForm, self).__init__(*args, **kwargs)
        pids = [p.advertiser.id for p in PublisherRelationship.objects.filter(publisher=org, status=RELATIONSHIP_ACCEPTED)]
        dfids = [d.advertiser.id for d in DataFeed.objects.filter(advertiser__id__in=pids)]
        self.fields['advertiser'].queryset = Organization.objects.filter(id__in=dfids)

    username = forms.CharField(label='Username', required=False)
    password = forms.CharField(label='Password', required=False)
    server = forms.CharField(label='Server', required=False)

    def clean_username(self):
        type = int(self.cleaned_data['datafeed_type'])
        if type == DATAFEEDTYPE_FTPPUSH:
            if 'username' not in self.cleaned_data or \
               not self.cleaned_data['username']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['username']

    def clean_password(self):
        type = int(self.cleaned_data['datafeed_type'])
        if type == DATAFEEDTYPE_FTPPUSH:
            if 'password' not in self.cleaned_data or \
               not self.cleaned_data['password']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['password']

    def clean_server(self):
        type = int(self.cleaned_data['datafeed_type'])
        if type == DATAFEEDTYPE_FTPPUSH:
            if 'server' not in self.cleaned_data or \
               not self.cleaned_data['server']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['server']
            

class PublisherDataTransferForm(SmartForm):

    format = forms.ChoiceField(label='Transfer Format', choices=PUB_DATAFEEDFORMAT_CHOICES)
    datafeed_type = forms.ChoiceField(label='Delivery Method', choices=PUB_DATAFEEDTYPE_CHOICES)
    
    def __init__(self, *args, **kwargs):
        org = kwargs.pop('org')
        super(PublisherDataTransferForm, self).__init__(*args, **kwargs)

    username = forms.CharField(label='Username', required=False)
    password = forms.CharField(label='Password', required=False)
    server = forms.CharField(label='Server', required=False)

    def clean_username(self):
        type = int(self.cleaned_data['datafeed_type'])
        if type == DATAFEEDTYPE_FTPPUSH:
            if 'username' not in self.cleaned_data or \
               not self.cleaned_data['username']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['username']

    def clean_password(self):
        type = int(self.cleaned_data['datafeed_type'])
        if type == DATAFEEDTYPE_FTPPUSH:
            if 'password' not in self.cleaned_data or \
               not self.cleaned_data['password']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['password']

    def clean_server(self):
        type = int(self.cleaned_data['datafeed_type'])
        if type == DATAFEEDTYPE_FTPPUSH:
            if 'server' not in self.cleaned_data or \
               not self.cleaned_data['server']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['server']    
                
class FilterForm(SmartForm):
    ''' Filter Form
    '''
    from atrinsic.base.models import PromotionMethod
    
    field = forms.ChoiceField(label='Filter:', choices=AUTODECLINEFIELD_CHOICES)
    value = forms.CharField(label='Value:', required=False)
    promotion_method = forms.ModelChoiceField(queryset=PromotionMethod.objects.order_by('name'), label='Promotion Method', required=False)
    publisher_vertical = forms.ChoiceField(label='Publisher Vertical', required=False)
    
    state = FormStateField(label='State', required=False)
    country = FormCountryField(label='Country', required=False)

    def clean_value(self):
        field = int(self.cleaned_data['field'])
        if field != AUTODECLINEFIELD_PROMOTION_METHOD and \
           field != AUTODECLINEFIELD_PUBLISHER_VERTICAL and \
           field != AUTODECLINEFIELD_COUNTRY  and \
           field != AUTODECLINEFIELD_STATE:
            if 'value' not in self.cleaned_data or \
               not self.cleaned_data['value']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['value']

    def clean_promotion_method(self):
        field = int(self.cleaned_data['field'])
        if field == AUTODECLINEFIELD_PROMOTION_METHOD:
            if 'promotion_method' not in self.cleaned_data or \
               not self.cleaned_data['promotion_method']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['promotion_method']

    def clean_publisher_vertical(self):
        field = int(self.cleaned_data['field'])
        if field == AUTODECLINEFIELD_PUBLISHER_VERTICAL:
            if 'publisher_vertical' not in self.cleaned_data or \
               not self.cleaned_data['publisher_vertical']:
                raise forms.ValidationError('This field is required')
            else:
                return self.cleaned_data['publisher_vertical']
    
    def __init__(self, organization, *args, **kwargs):
        from atrinsic.base.models import PublisherVertical
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['publisher_vertical'].choices = [(a.order, a.name) for a in PublisherVertical.objects.order_by('name').filter(is_adult=organization.is_adult)]
        


class LinkForm(SmartForm):
    ''' Base Link Form
    '''
    from atrinsic.base.models import LinkPromotionType
    
    link_choices = [  ]
    link_choices.extend([ (v.order, v.name) for v in LinkPromotionType.objects.all().order_by('name') ])
    
    onedit = False

    name = forms.CharField(label='Link Name', max_length=256)
    start_date = forms.DateField(label='Start Date:', widget = DateFormattedTextInput)
    end_date = forms.DateField(label='End Date:',required=False, widget = DateFormattedTextInput)

    #link_promotion_type = forms.ChoiceField(choices=link_choices, label='Promotion Type', required=False)
    link_promotion_type = forms.ModelChoiceField(
        queryset=LinkPromotionType.objects.all().order_by('name'),
        label='Promotion Type',
        required=False
    )

    assigned_to = forms.ChoiceField(label='Assigned To', choices=LINKASSIGNED_CHOICES, required=False)

    assigned_to_program_term = forms.ChoiceField(label='Program Term', required=False)
    assigned_to_group = forms.ChoiceField(label='Publisher Group', required=False)
    assigned_to_individual = forms.ChoiceField(label='Organization', required=False)
    assigned_to_minimum_rating = forms.FloatField(label='Minimum Rating', required=False)
    assigned_to_promotion_method = forms.ChoiceField(label='Promotion Method', required=False)
    assigned_to_publisher_vertical = forms.ChoiceField(label='Publisher Vertical', required=False)

    def __init__(self, organization, *args, **kwargs):
        is_edit = kwargs.pop('is_edit', False)
        super(LinkForm, self).__init__(*args, **kwargs)
        if is_edit and 'image' in self.fields:
            self.fields['image'].required = False

        if is_edit:
            self.onedit = True

        from atrinsic.base.models import Organization,PromotionMethod,PublisherVertical
        self.organization = organization

        self.fields['assigned_to_program_term'].choices = [(cl.id, cl.name) for cl in self.organization.programterm_set.all()]
        self.fields['assigned_to_individual'].choices = [ (o.id, o.name) for o in Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED, advertiser_relationships__advertiser=self.organization).order_by('company_name')]

        self.fields['assigned_to_group'].choices = [ (g.id, g.name) for g in self.organization.publisher_groups.all() ]

        self.fields['assigned_to_promotion_method'].choices = [ (m.order, m.name) for m in PromotionMethod.objects.all().order_by('name') ]

        self.fields['assigned_to_publisher_vertical'].choices = [ (v.order, v.name) for v in PublisherVertical.objects.filter(is_adult=organization.is_adult).order_by('name') ]
        
        
    def clean_link_promotion_type(self):
        from atrinsic.base.models import LinkPromotionType
        promo = None
        id = self.cleaned_data.get('link_promotion_type', None)
        if isinstance(id, LinkPromotionType):
            return id

        if id:
            try:
                promo = LinkPromotionType.objects.get(order=id)
            except LinkPromotionType.DoesNotExist:
                raise forms.ValidationError(u'Unknown Link Promotion Type: %s' % id)

        return promo

    def clean_assigned_to_program_term(self):
        from atrinsic.base.models import ProgramTerm
        cl = self.cleaned_data.get('assigned_to_program_term', None)
        assigned_to = int(self.cleaned_data.get('assigned_to', 0))

        if assigned_to == LINKASSIGNED_PROGRAM_TERM:
            try:
                cl = self.organization.programterm_set.get(id=cl)
            except ProgramTerm.DoesNotExist:
                raise forms.ValidationError(u'Select a Program Term')
        else:
            cl = None

        return cl

    def clean_assigned_to_individual(self):
        from atrinsic.base.models import Organization
        o = self.cleaned_data.get('assigned_to_individual', None)
        assigned_to = int(self.cleaned_data.get('assigned_to', 0))

        if assigned_to == LINKASSIGNED_INDIVIDUAL:
            try:
                o = Organization.objects.get(advertiser_relationships__status=RELATIONSHIP_ACCEPTED, advertiser_relationships__advertiser=self.organization, id=o)
            except Organization.DoesNotExist:
                raise forms.ValidationError(u'Select an Organization')
        else:
            o = None

        return o

    def clean_assigned_to_group(self):
        from atrinsic.base.models import PublisherGroup
        g = self.cleaned_data.get('assigned_to_group', None)
        assigned_to = int(self.cleaned_data.get('assigned_to', 0))

        if assigned_to == LINKASSIGNED_GROUP:
            try:
                g = self.organization.publisher_groups.get(id=g)
            except PublisherGroup.DoesNotExist:
                raise forms.ValidationError(u'Select a Publisher Group')
        else:
            g = None

        return g

    def clean_assigned_to_publisher_vertical(self):
        from atrinsic.base.models import PublisherVertical
        v = self.cleaned_data.get('assigned_to_publisher_vertical', None)
        assigned_to = int(self.cleaned_data.get('assigned_to', 0))

        if assigned_to == LINKASSIGNED_PUBLISHER_VERTICAL:
            try:
                v = PublisherVertical.objects.get(order=v)
            except PublisherVertical.DoesNotExist:
                raise forms.ValidationError(u'Select a Vertical')
        else:
            v = None

        return v

    def clean_assigned_to_promotion_method(self):
        from atrinsic.base.models import PromotionMethod
        m = self.cleaned_data.get('assigned_to_promotion_method', None)
        assigned_to = int(self.cleaned_data.get('assigned_to', 0))

        if assigned_to == LINKASSIGNED_PROMOTION_METHOD:
            try:
                m = PromotionMethod.objects.get(order=m)
            except PromotionMethod.DoesNotExist:
                raise forms.ValidationError(u'Select a Promotion Method')
        else:
            m = None

        return m

    def clean_assigned_to_minimum_rating(self):
        rating = self.cleaned_data.get('assigned_to_minimum_rating', 0)
        assigned_to = int(self.cleaned_data.get('assigned_to', 0))

        if assigned_to == LINKASSIGNED_MINIMUM_RATING:
            if rating is None:
                raise forms.ValidationError(u'Enter a rating')

            try:
                rating = str(float(rating))
            except:
                raise forms.ValidationError(u'Enter a valid rating')
        else:
            rating = None 

        return rating

class TextLinkForm(LinkForm):
    ''' Text Link Form
    '''

    class Meta:
        layout =  ("name", "link_promotion_type", "assigned_to", "assigned_to_program_term", 
                     "assigned_to_group", "assigned_to_individual", "assigned_to_minimum_rating",
                     "assigned_to_promotion_method", "assigned_to_publisher_vertical", "start_date", "end_date", 
                     "link_content", "landing_page_url")


    link_content= forms.CharField(max_length=4096, label='Link Content', widget=forms.Textarea)
    landing_page_url = forms.CharField(label='Landing Page URL')
    
    def clean(self):
        from atrinsic.base.models import Link
        if not self.onedit:
            current_banner_total = Link.objects.filter(link_type=LINKTYPE_TEXT, advertiser=self.organization).count()
            if int(self.organization.allowed_text) <= int(current_banner_total) :
                raise forms.ValidationError(u'Maximum amount of links for this type has been created')
            else:
                return self.cleaned_data
        else:
            return self.cleaned_data   

class RssLinkForm(LinkForm):
    ''' Rss Link Form
    '''

    class Meta:
        layout =  ("name", "link_promotion_type", "assigned_to", "assigned_to_program_term", 
                     "assigned_to_group", "assigned_to_individual", "assigned_to_minimum_rating",
                     "assigned_to_promotion_method", "assigned_to_publisher_vertical", "start_date", "end_date", 
                     "link_content", "landing_page_url")


    #link_content= forms.CharField(max_length=4096, label='Link Content', widget=forms.Textarea)
    landing_page_url = forms.URLField(label='Landing Page URL')
    link_content = forms.CharField(label='RSS Feed Link')
    
    def clean(self):
        from atrinsic.base.models import Link
        if not self.onedit:
            current_banner_total = Link.objects.filter(link_type=LINKTYPE_RSS, advertiser=self.organization).count()
            if int(self.organization.allowed_rss) <= int(current_banner_total) :
                raise forms.ValidationError(u'Maximum amount of links for this type has been created')
            else:
                return self.cleaned_data
        else:
            return self.cleaned_data
            
class HtmlLinkForm(LinkForm):
    ''' Text Link Form
    '''

    class Meta:
        layout =  ("name", "link_promotion_type", "assigned_to", "assigned_to_program_term", 
                     "assigned_to_group", "assigned_to_individual", "assigned_to_minimum_rating",
                     "assigned_to_promotion_method", "assigned_to_publisher_vertical",
                     "start_date", "end_date", "link_content", "landing_page_url")


    link_content= forms.CharField(max_length=4096, label='Link Content', widget=forms.Textarea)
    landing_page_url = forms.CharField(label='Landing Page URL')
    
    def clean(self):
        from atrinsic.base.models import Link
        if not self.onedit:
            current_banner_total = Link.objects.filter(link_type=LINKTYPE_HTML, advertiser=self.organization).count()
            if int(self.organization.allowed_html) <= int(current_banner_total) :
                raise forms.ValidationError(u'Maximum amount of links for this type has been created')
            else:
                return self.cleaned_data
        else:
            return self.cleaned_data   
            
class KeywordLinkForm(LinkForm):
    ''' Keyword Link Form
    '''

    class Meta:
        layout =  ("name", "link_promotion_type", "assigned_to", "assigned_to_program_term", 
                     "assigned_to_group", "assigned_to_individual", "assigned_to_minimum_rating",
                     "assigned_to_promotion_method", "assigned_to_publisher_vertical", 
                     "start_date", "end_date", "usage_recommendations", "protected_keyword_list", 
                     "recommended_keywords", "noncompete_keywords", "landing_page_url")

    usage_recommendations = forms.CharField(max_length=4096, label='Usage Recommendations', widget=forms.Textarea)
    protected_keyword_list = forms.CharField(max_length=4096, label='Protected Keyword List', widget=forms.Textarea)
    recommended_keywords = forms.CharField(max_length=4096, label='Recommended Keywords', widget=forms.Textarea)
    noncompete_keywords = forms.CharField(max_length=4096, label='Non-Compete Keywords', widget=forms.Textarea)
    landing_page_url = forms.CharField(label='Landing Page URL')
    
    def clean(self):
        from atrinsic.base.models import Link
        if not self.onedit:
            current_banner_total = Link.objects.filter(link_type=LINKTYPE_KEYWORD, advertiser=self.organization).count()
            if int(self.organization.allowed_keyword) <= int(current_banner_total) :
                raise forms.ValidationError(u'Maximum amount of links for this type has been created')
            else:
                return self.cleaned_data
        else:
            return self.cleaned_data           

class EmailLinkForm(LinkForm):
    ''' Email Link Form
    '''

    class Meta:
        layout =  ("name", "link_promotion_type", "assigned_to", "assigned_to_program_term", 
                     "assigned_to_group", "assigned_to_individual", "assigned_to_minimum_rating",
                     "assigned_to_promotion_method", "assigned_to_publisher_vertical", 
                     "start_date", "end_date", "link_content", "html_content", "suppression_list", "landing_page_url")


    link_content = forms.CharField(label='Text Content', widget=forms.Textarea)
    html_content = forms.CharField(label='HTML Content', widget=forms.Textarea)
    landing_page_url = forms.URLField(label='Landing Page URL')
    suppression_list = forms.FileField(label='Suppression List', required=False)
    def clean(self):
        from atrinsic.base.models import Link
        if not self.onedit:
            current_banner_total = Link.objects.filter(link_type=LINKTYPE_EMAIL, advertiser=self.organization).count()
            if int(self.organization.allowed_email_link) <= int(current_banner_total) :
                raise forms.ValidationError(u'Maximum amount of links for this type has been created')
            else:
                return self.cleaned_data
        else:
            return self.cleaned_data        

class FlashLinkForm(LinkForm):
    ''' Flash Link Form
    '''

    class Meta:
        layout =  ("name", "link_promotion_type", "landing_page_url",
                     "assigned_to", "assigned_to_program_term", 
                     "assigned_to_group", "assigned_to_individual", "assigned_to_minimum_rating",
                     "assigned_to_promotion_method", "assigned_to_publisher_vertical",
                     "start_date", "end_date", "swf_width", "swf_height", "swf_file")
    landing_page_url = forms.CharField(label='Landing Page URL')
    swf_file = forms.FileField(label='SWF File', required=True)
    #html_content = forms.CharField(label='HTML Content', widget=forms.Textarea, required=False)
    swf_width = forms.IntegerField(label='Width (px)', required=True)    
    swf_height = forms.IntegerField(label='Height (px)', required=True)    
    
    def clean(self):
        from atrinsic.base.models import Link
        if not self.onedit:
            current_banner_total = Link.objects.filter(link_type=LINKTYPE_FLASH, advertiser=self.organization).count()
            if int(self.organization.allowed_flash) <= int(current_banner_total) :
                raise forms.ValidationError(u'Maximum amount of links for this type has been created')
            else:
                return self.cleaned_data
        else:
            return self.cleaned_data
            
class editFlashLinkForm(LinkForm):
    ''' Flash Link Form
    '''

    class Meta:
        layout =  ("name", "link_promotion_type", "landing_page_url",
                     "assigned_to", "assigned_to_program_term", 
                     "assigned_to_group", "assigned_to_individual", "assigned_to_minimum_rating",
                     "assigned_to_promotion_method", "assigned_to_publisher_vertical",
                     "start_date", "end_date", "swf_width", "swf_height", "swf_file")
    landing_page_url = forms.CharField(label='Landing Page URL')
    swf_file = forms.FileField(label='SWF File', required=False)
    #html_content = forms.CharField(label='HTML Content', widget=forms.Textarea, required=False)
    swf_width = forms.IntegerField(label='Width (px)', required=True)    
    swf_height = forms.IntegerField(label='Height (px)', required=True)    
    
    def clean(self):
        from atrinsic.base.models import Link
        if not self.onedit:
            current_banner_total = Link.objects.filter(link_type=LINKTYPE_FLASH, advertiser=self.organization).count()
            if int(self.organization.allowed_flash) <= int(current_banner_total) :
                raise forms.ValidationError(u'Maximum amount of links for this type has been created')
            else:
                return self.cleaned_data
        else:
            return self.cleaned_data
class BannerLinkForm(LinkForm):
    ''' Banner Link Form
    '''

    class Meta:
        layout =  ("name", "link_promotion_type", "assigned_to", "assigned_to_program_term", 
                     "assigned_to_group", "assigned_to_individual", "assigned_to_minimum_rating",
                     "assigned_to_promotion_method", "assigned_to_publisher_vertical", 
                     "start_date", "end_date", "landing_page_url", "image", "banner_url")

    ad_image_id = forms.IntegerField(widget=forms.HiddenInput(),required=False)
    image = forms.ImageField(label='Upload Banner Image:', required=False)
    banner_url = forms.URLField(verify_exists=False, label='Select Hosted Image:', required=False)
    landing_page_url = forms.CharField(label='Landing Page URL:')

    def clean(self):
        from atrinsic.base.models import Link
        if not self.onedit:
            current_banner_total = Link.objects.filter(link_type=LINKTYPE_BANNER, advertiser=self.organization).count()
            if int(self.organization.allowed_banner) <= int(current_banner_total) :
                raise forms.ValidationError(u'Maximum amount of links for this type has been created')
            else:
                return self.cleaned_data
        else:
            return self.cleaned_data

class GetLinkWebsiteForm(SmartForm):
    ''' Select a Website to get a Link from '''

    website = forms.ChoiceField(label='Select a Web Site',choices=[])
    
    def __init__(self, organization, *args, **kwargs):
        super(GetLinkWebsiteForm, self).__init__(*args, **kwargs)
        from atrinsic.base.models import Website
        self.fields['website'].choices = [(w.id, w.url) for w in Website.objects.filter(publisher=organization) ]

class GetLinkForm(SmartForm):
    ''' Base GetLink Form
    '''
   
    vertical = forms.MultipleChoiceField(label='Find By Vertical', required=False)

    def __init__(self, organization, *args, **kwargs):
        from atrinsic.base.models import PublisherVertical
        super(GetLinkForm, self).__init__(*args, **kwargs)
        vc = [('-1', 'All Verticals')]
        vc.extend([ (v.order, v.name) for v in PublisherVertical.objects.order_by('name').filter(is_adult=organization.is_adult) ])
        self.fields['vertical'].choices = vc


class GetBannerLinkForm(GetLinkForm):
    ''' Form to get a Banner Link
    '''
    from atrinsic.base.models import BannerSize
    
    class Meta:
        layout = (
            Fieldset("Banner Information", "vertical", "size", ),
        )
    
    size = forms.MultipleChoiceField(label='Banner Size', choices=[ (s.order, s.name) for s in BannerSize.objects.all().order_by('name') ], required=False)
    
        
class GetKeywordLinkForm(GetLinkForm):
    class Meta:
        layout = (
            Fieldset("Keyword Link Search", "vertical", ),
            Fieldset("Settings", "allow_third_party_email_campaigns", "allow_direct_linking_through_ppc", 
                     "allow_trademark_bidding_through_ppc", ),
        )

    allow_third_party_email_campaigns = forms.BooleanField(label='Allow Third Party Email Campaigns?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]), required=False)

    allow_direct_linking_through_ppc = forms.BooleanField(label='Allow Direct Linking Through PPC?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]), required=False)

    allow_trademark_bidding_through_ppc = forms.BooleanField(label='Allow Trademark Bidding Through PPC?',
        widget=forms.widgets.RadioSelect(choices=[('1', 'Yes'), ('0', 'No')]), required=False)


class GetTextLinkForm(GetLinkForm):
    class Meta:
        layout = (
        	Fieldset("Text Link Search", "vertical", "link_promotion_type"),
        )        
    from atrinsic.base.models import LinkPromotionType
    
    pc = [('-1', 'All Promotion Types')]
    pc.extend([ (p.order, p.name) for p in LinkPromotionType.objects.all().order_by('name') ])

    link_promotion_type = forms.MultipleChoiceField(choices=pc, label='Promotion Type', required=False)

class GetHtmlLinkForm(GetLinkForm):
    class Meta:
        layout = (
            Fieldset("Html Link Search", "vertical", "link_promotion_type"),
        )
    from atrinsic.base.models import LinkPromotionType
    
    pc = [('-1', 'All Promotion Types')]
    pc.extend([ (p.order, p.name) for p in LinkPromotionType.objects.all().order_by('name') ])

    link_promotion_type = forms.MultipleChoiceField(choices=pc, label='Promotion Type', required=False)


class GetFlashLinkForm(GetLinkForm):
    class Meta:
        layout = (
            Fieldset("Flash Link Search", "vertical", ),
        )

class GetEmailLinkForm(GetLinkForm):
    class Meta:
        layout = (
            Fieldset("Email Link Search", "vertical", ),
        )

class GetRssLinkForm(GetLinkForm):
    class Meta:
        layout = (
            Fieldset("Rss Feed Search", "vertical", ),
        )
        
class PublisherSearchForm(SmartForm):
    ''' Search Form
    '''

    class Meta:
        layout = ("q", "date_from", "date_to", "vertical" )

    q = forms.CharField(max_length=256, label='Company Name:', required=False)
    pub_id = forms.CharField(max_length=256, label='Publisher ID', required=False)
    pub_url = forms.CharField(max_length=4096, label='Publisher URL', required=False)
    date_from = forms.DateField(label='Joined Between:', required=False, widget = DateFormattedTextInput)
    date_to= forms.DateField(label='', required=False, widget = DateFormattedTextInput)
    #vertical = forms.MultipleChoiceField(label='Category', required=False, choices=choices)
    vertical = forms.ChoiceField(label='Category:', required=False)
    #force = forms.FloatField(label='Force > than', required=False)
    #network_rating = forms.FloatField(label='Rating:', required=False)


    def __init__(self, organization, *args, **kwargs):
        from atrinsic.base.models import PublisherVertical
        super(PublisherSearchForm, self).__init__(*args, **kwargs)
        vc = [('-1', 'All Verticals')]
        vc.extend([ (v.order, v.name) for v in PublisherVertical.objects.order_by('name').filter(is_adult=organization.is_adult) ])
        self.fields['vertical'].choices = vc


class GroupCreateForm(SmartForm):
    ''' Create a Group
    '''

    name = forms.CharField(max_length=256, label='Create A New Group')

class GroupAddtoForm(SmartForm):
    group = forms.ChoiceField(label='Select a Group')

    def __init__(self, organization, *args, **kwargs):
        from atrinsic.base.models import PublisherGroup
        super(GroupAddtoForm, self).__init__(*args, **kwargs)
        self.fields['group'].choices = [(g.id, g.name) for g in PublisherGroup.objects.filter(advertiser=organization)]


class GroupAddMembersForm(SmartForm):
    ''' Create a Group
    '''

    group_id = forms.IntegerField(label="Group Id")
    publisher_id = forms.IntegerField(label="Group Members")


class PasswordResetForm(SmartForm):
    class Meta:
        layout = (
            Fieldset("Reset Password", "password", "password2"),
        )
            
    password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    
    def clean_password2(self):
        p = self.cleaned_data.get('password', None)
        p2 = self.cleaned_data.get('password2', None)

        if p != p2:
            raise forms.ValidationError(u'Passwords do not match')

        return p2

class ForgotPasswordForm(SmartForm):
    ''' Forgot Password Form
    '''

    forgot_email = forms.CharField(max_length=256, label="Enter Your Email Address To Reset Password", required=False)

    def clean_forgot_email(self):
        from atrinsic.base.models import User
        print "Validating password forget form"
        forgot_email = self.cleaned_data.get('forgot_email', None)
        print forgot_email
        if forgot_email is None or len(forgot_email) < 1:
            return None

        if User.objects.filter(email=forgot_email).count() < 1:
            print "Not Registerd"
            raise forms.ValidationError(u'This E-Mail is not registered.')
            
        try:    
            user =  User.objects.get(email=forgot_email)
            if user:
                if user.get_profile().organizations.filter(status=ORGSTATUS_LIVE).count() < 1:
                    raise forms.ValidationError(u'This E-Mail is not registered to an active account.')
        except:
            raise forms.ValidationError(u'This E-Mail is not registered to an active account.')
            
       
        return forgot_email


class LoginForm(SmartForm):
    ''' Login Authentication Form
    '''
    class Meta:
        layout = ('email', 'password', )

    email = forms.CharField(max_length=256, label='E-Mail')
    password = forms.CharField(max_length=256, label='Password', widget=forms.PasswordInput)

class StatusUpdateForm(SmartForm):
    ''' Status Update Form    '''
    class Meta:
        layout = (
           'message', 
        )
    
    #receiver = forms.CharField(max_length=256, label="To", required=False)
    #subject = forms.CharField(max_length=256, label="Subject", required=False)
    message = forms.CharField(max_length=140, min_length=10, widget=forms.Textarea, label='Status')


class PrivateMessageForm(SmartForm):
    ''' Private Message Form
    '''

    class Meta:
        layout = (
            Fieldset('Compose Message', 'receiver', 'subject', 'message', ),
        )

    receiver = forms.CharField(max_length=256, label="To")
    subject = forms.CharField(max_length=256, label="Subject")
    message = forms.CharField(max_length=4096, min_length=10, widget=forms.Textarea, label='Message')
    
    def clean_receiver(self):
        from atrinsic.base.models import Organization
        name  = self.cleaned_data.get('receiver', None)

        if name and name.lower() == 'multiple recipients':
            return True

        receiver = None

        try:
            receiver = Organization.objects.get(company_name=name)
        except:
            try:
                receiver = Organization.objects.get(company_alias=name)
            except:
                raise forms.ValidationError(u'Unknown Organization')

        return receiver

class PublisherPrivateMessageForm(SmartForm):
    ''' Publisher Private Message Form
    '''

    receiver = forms.ChoiceField(label="To")
    subject = forms.CharField(max_length=256, label="Subject")
    message = forms.CharField(max_length=4096, min_length=10, widget=forms.Textarea, label='Message')

    def clean_receiver(self):
        from atrinsic.base.models import Organization
        id = self.data.get('receiver', None)

        if Organization.objects.filter(id=id).count() < 1:
            raise forms.ValidationError(u'Unknown Organization')

        return id
 
    def __init__(self, *args, **kwargs):
        from atrinsic.base.models import PublisherRelationship, Organization
        org = kwargs.pop('org')
        super(PublisherPrivateMessageForm, self).__init__(*args, **kwargs)
        #self.fields['receiver'].choices = \
        #        ((u.advertiser.id, u.advertiser.name) for u in PublisherRelationship.objects.filter(publisher=org,status=RELATIONSHIP_ACCEPTED, publisher__status = ORGSTATUS_LIVE))
        self.fields['receiver'].choices = \
                    ((u.id, u.name) for u in Organization.objects.all().extra(where=[' id IN (select advertiser_id from base_publisherrelationship where publisher_id = ' + str(org.id) + ' and status = ' + str(ORGSTATUS_LIVE) + ') order by if(show_alias = 1, company_alias, company_name)']))
        #.extra(where=[' id IN (select advertiser_id from base_publisherrelationship where publisher_id = ' + org.id + ' and status = ' + ORGSTATUS_LIVE + )'])
        #' if(show_alias = 1, company_alias, company_name)'

class AdvertiserPrivateMessageForm(SmartForm):
    ''' Publisher Private Message Form
    '''
    receiver = forms.ChoiceField(label="To")
    subject = forms.CharField(max_length=256, label="Subject")
    message = forms.CharField(max_length=4096, min_length=10, widget=forms.Textarea, label='Message')

    def clean_receiver(self):
        from atrinsic.base.models import Organization
        id = self.data.get('receiver', None);
        if Organization.objects.filter(id=id).count() < 1:
            raise forms.ValidationError(u'Unknown Organization')

        return id
 
    def __init__(self, *args, **kwargs):
        from atrinsic.base.models import Organization
        org = kwargs.pop('org')
        super(AdvertiserPrivateMessageForm, self).__init__(*args, **kwargs)
        #self.fields['receiver'].choices = \
        #        ((u.publisher.id, u.publisher.name) for u in PublisherRelationship.objects.filter(advertiser=org,status=RELATIONSHIP_ACCEPTED, publisher__status = ORGSTATUS_LIVE))
        self.fields['receiver'].choices = \
                ((u.id, u.name) for u in Organization.objects.all().extra(where=[' id IN (select publisher_id from base_publisherrelationship where advertiser_id = ' + str(org.id) + ' and status = ' + str(ORGSTATUS_LIVE) + ') order by if(show_alias = 1, company_alias, company_name)']))

class OrganizationEditForm(SmartForm):
    ''' Organization Form
    '''

    name = forms.CharField(max_length=256, label='Organization Name')

    address = forms.CharField(max_length=256, label='Address')
    address2 = forms.CharField(max_length=256, label='', required=False)
    city = forms.CharField(max_length=256, label='City')
    state = FormStateField(label='State')
    zipcode = forms.CharField(max_length=256, label='Zipcode')

class LoginEditForm(SmartForm):
    ''' Login Form to validate e-mail address and password
    '''

    first_name = forms.CharField(max_length=256, label='First Name')
    last_name = forms.CharField(max_length=256, label='Last Name')

    email = forms.EmailField(max_length=256, label='E-mail Address')

    password = forms.CharField(max_length=256, label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=256, label='Confirm Password', widget=forms.PasswordInput)

    def clean_password2(self):
        p = self.cleaned_data.get('password', None)
        p2 = self.cleaned_data.get('password2', None)

        if p != p2:
            raise forms.ValidationError(u'Passwords do not match')

        return p2

class BulkUploadForm(SmartForm):
    ''' Bulk upload XLS file Form
    '''
    upload_action = forms.ChoiceField(label='Upload Action', choices=[(1,'Bulk Add'),
                                                                      (2,'Bulk Update'),
                                                                      (3,'Bulk Delete')])

    upload_type = forms.ChoiceField(label='Upload Type', choices=[(1,'Upload for availablity to all approved'),
                                                                  (2,'Upload for availablity to individual publishers')])


    confirmation_email = forms.EmailField(max_length=256, label='Confirmation E-Mail')
    bulk_file = forms.FileField()



class OrganizationForm(SmartModelForm):
    
    class Meta:
        from atrinsic.base.models import Organization
        model = Organization

        fields = ('company_name', 'address', 'address2', 'city', 'state', 'zipcode', 
        )

        layout = ("company_name", "address", "address2", "city", "state", "zipcode", )


class WelcomeEmailForm(SmartForm):
    ''' Welcome Email Form
    '''

    class Meta:
        layout = (
            Fieldset('Welcome Email', 'subject', 'body', 'html_body', ),
        )
    
    subject = forms.CharField(max_length=256, label='Subject')
    body = forms.CharField(label='Text Message', widget=forms.Textarea(attrs={'rows': 15, }))
    html_body = forms.CharField(label='HTML Message', widget=forms.Textarea(attrs={'rows': 15, }))

class EmailCampaignForm(SmartForm):
    ''' Campaign Creation Form
    '''

    name = forms.CharField(label='Campaign Name')
    email_from = forms.ChoiceField(label='Email From', choices=(('',''),))
    reply_to_address = forms.ChoiceField(label='Reply To', choices=(('',''),))
    date_send = forms.DateField(label='Send Date', required=False, widget = DateFormattedTextInput)

    subject = forms.CharField(max_length=256, label='Subject')

    body = forms.CharField(max_length=1024 * 10, label='Text Message', widget=forms.Textarea(attrs={'rows': 15, }))
    html_body = forms.CharField(max_length=1024 * 10, label='HTML Message', widget=forms.Textarea(attrs={'rows': 15, }))

    def __init__(self, *args, **kwargs):
        org = kwargs.pop('org')
        from atrinsic.base.models import UserProfile
        super(EmailCampaignForm, self).__init__(*args, **kwargs)
        self.fields['email_from'].choices = \
            ((u.user.email, u.user.email) for u in UserProfile.objects.filter(organizations__id=org.id))
        self.fields['reply_to_address'].choices = \
            ((u.user.email, u.user.email) for u in UserProfile.objects.filter(organizations__id=org.id))

    class Meta:
        fields = ('name', 'email_from', 'reply_to_address', 'subject',
                  'body', 'html_body', 'date_send')
        layout = ("name", "email_from", "reply_to_address", "date_send", "subject", "body", "html_body")


class EmailCampaignCriteriaForm(SmartForm):
    ''' Campaign Criteria Form
    '''

    class Meta:
        layout = ("time_period", "alert_field","field_is_less_than_threshold", "threshold")
    time_period = forms.ChoiceField(label='Time Period', choices=CAMPAIGNCRITERIAPERIOD_CHOICES)
    alert_field = forms.ChoiceField(label='Alert Field', choices=METRIC_CHOICES)

    field_is_less_than_threshold = forms.BooleanField(label='Method',
            widget=forms.widgets.RadioSelect(choices=[('0', 'Less Than'), ('1', 'Greater Than or Equal To')])) 

    threshold = forms.IntegerField(label='Threshold')    

class AdvertiserImageForm(SmartForm):
    image = forms.FileField(label="Browse Image to Upload:")


class AdvertiserImageBulkForm(SmartForm):
    file = forms.FileField(label="Browse Multiple Images to Upload")
    confirmation_email = forms.EmailField(max_length=256, label='Confirmation E-Mail')
    
    def clean_file(self):
        if 'file' in self.cleaned_data:
            file = self.cleaned_data['file']
            try:
                ext = os.path.splitext(file.name)[1]
            except IndexError:
                raise forms.ValidationError('Zip file is required')

            if ext != '.zip':
                raise forms.ValidationError('Zip file is required')

            return file
        raise forms.ValidationError('This field is required')


class ReportForm(SmartForm):
    class Meta:
        layout =  (
            Fieldset("Report Metrics", "start_date", "end_date", "group_by", "run_reporting_by", "run_reporting_by_group", "run_reporting_by_vertical", "run_reporting_by_publisher", "report_type"),
        )

    import datetime
    year = datetime.datetime.now().year
    group_by = forms.ChoiceField(label='Group By:', widget=forms.widgets.RadioSelect, choices=REPORTGROUPBY_CHOICES[:-1])
    run_reporting_by = forms.ChoiceField(label='Run Reporting By:',widget=forms.widgets.RadioSelect(attrs={'class':'run_reports_by'}),choices=RUNREPORTBY_CHOICES)
    run_reporting_by_group = forms.MultipleChoiceField(label='Select Group',required=False)
    run_reporting_by_vertical = forms.MultipleChoiceField(label='Select Vertical', required=False)
    run_reporting_by_publisher = forms.MultipleChoiceField(label='Select Publishers',required=False)
    report_type = forms.ChoiceField(label='Report Type:', choices=REPORTTYPE_CHOICES)

    start_date = forms.DateField(label='Start Date:',required=False, widget = DateFormattedTextInput)
    end_date = forms.DateField(label='End Date',required=False, widget = DateFormattedTextInput)

    def __init__(self, organization, *args, **kwargs):
        from atrinsic.base.models import PublisherVertical
        super(ReportForm, self).__init__(*args, **kwargs)
        self.populate_fields(organization)
        vc = []
        vc.extend([ (v.order, v.name) for v in PublisherVertical.objects.order_by('name').filter(is_adult=organization.is_adult) ])
        self.fields['run_reporting_by_vertical'].choices = vc
        
    def populate_fields(self,organization):
        from atrinsic.base.models import Organization
        self.fields['run_reporting_by_group'].choices = [ ('g_%d' % g.id, g.name) for g in organization.publisher_groups.all() ]
        self.fields['run_reporting_by_publisher'].choices = [ ('p_%d' % p.id, p.name) for p in Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED, advertiser_relationships__advertiser=organization) ]


class ReportFormPublisher(SmartForm):
    class Meta:
        layout =  ("start_date", "end_date", "group_by", "run_reporting_by", "advertiser_category","specific_advertiser","report_type" )
        
    import datetime
   
    group_by = forms.ChoiceField(label='Group By',widget=forms.widgets.RadioSelect(attrs={'class':'group_by'}), choices=REPORTGROUPBY_CHOICES)
    run_reporting_by = forms.ChoiceField(label='Run Reporting By', widget=forms.widgets.RadioSelect(attrs={'class':'run_reports_by'}),choices=(('0','All Advertisers'),('1','Advertiser'),('2','Vertical')))
    advertiser_category = forms.MultipleChoiceField(label='Advertiser Category', widget=forms.SelectMultiple,required=False)
    specific_advertiser = forms.ChoiceField(label='Specific Advertiser', required=False)
    report_type = forms.ChoiceField(label='Report Type', choices=REPORTTYPE_CHOICES_PUBLISHER)

    start_date = forms.DateField(label='Time period',required=True, widget = DateFormattedTextInput)
    end_date = forms.DateField(label='End Date',required=False, widget = DateFormattedTextInput)

    def __init__(self, organization, *args, **kwargs):
        from atrinsic.base.models import PublisherVertical
        super(ReportFormPublisher, self).__init__(*args, **kwargs)
        self.populate_fields(organization)
        vc = []
        vc.extend([ (v.order, v.name) for v in PublisherVertical.objects.order_by('name').filter(is_adult=organization.is_adult) ])
        self.fields['advertiser_category'].choices = vc
        
    
    def populate_fields(self,organization):
        from atrinsic.base.models import Organization
        self.fields['specific_advertiser'].choices = [('a_%d' % a.id, a.name) for a in Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_ACCEPTED, publisher_relationships__publisher=organization).extra(where=[' 1 = 1 order by if(show_alias = 1, company_alias, company_name)'])]

class ReportFormNetworkAdvertiser(SmartForm):
    class Meta:
        layout =  (
            "start_date", "end_date", "group_by", "report_type", "run_reporting_by", "advertiser_category","specific_advertiser",
        )
    import datetime
    from atrinsic.base.models import PublisherVertical
    
    group_by = forms.ChoiceField(label='Group By :', choices=REPORTGROUPBY_CHOICES)
    run_reporting_by = forms.ChoiceField(label='Display By :',choices=(('0','All Advertisers'),('1','Individual Advertiser'),('2','Advertiser Primary Category')))
    advertiser_category = forms.ModelMultipleChoiceField(label='Advertiser Category :', widget=forms.SelectMultiple,required=False,queryset=PublisherVertical.objects.all())
    specific_advertiser = forms.ChoiceField(label='Specific Advertiser :', required=False)
    report_type = forms.ChoiceField(label='Report Type :', choices=REPORTTYPE_CHOICES)

    start_date = forms.DateField(label='Start Date :',required=False, widget = DateFormattedTextInput)
    end_date = forms.DateField(label='End Date :',required=False, widget = DateFormattedTextInput)

    def __init__(self, user, *args, **kwargs):
        super(ReportFormNetworkAdvertiser, self).__init__(*args, **kwargs)
        self.populate_fields(user)
    
    def populate_fields(self,user):
        self.fields['specific_advertiser'].choices = [('a_%d' % a.id, a.name) for a in user.get_profile().admin_assigned_advertisers() ]


class ReportFormNetworkPublisher(SmartForm):
    class Meta:
        layout =  (
            "start_date", "end_date", "group_by", "report_type", "run_reporting_by", "publisher_vertical","specific_publisher",
        )
    from atrinsic.base.models import PublisherVertical
    import datetime
    
    start_date = forms.DateField(label='Start Date :',required=False, widget = DateFormattedTextInput)
    end_date = forms.DateField(label='End Date :',required=False, widget = DateFormattedTextInput)
    group_by = forms.ChoiceField(label='Group By :', choices=REPORTGROUPBY_CHOICES[:-1])
    run_reporting_by = forms.ChoiceField(label='Display By :',choices=(('0','All Publishers'),('1','Individual Publisher'),('2','Publisher Primary Category')))
    publisher_vertical = forms.ModelMultipleChoiceField(label='Publisher Category :', widget=forms.SelectMultiple,required=False,queryset=PublisherVertical.objects.all())
    specific_publisher = forms.ChoiceField(label='Specific Publisher :', required=False)
    report_type = forms.ChoiceField(label='Report Type :', choices=REPORTTYPE_CHOICES_PUBLISHER)

    def __init__(self, user, *args, **kwargs):
        super(ReportFormNetworkPublisher, self).__init__(*args, **kwargs)
        self.populate_fields(user)
    
    def populate_fields(self,user):
        self.fields['specific_publisher'].choices = [('p_%d' % p.id, p.name) for p in user.get_profile().admin_assigned_publishers() ]


        
class PublisherPageForm(SmartModelForm):
    class Meta:
        from atrinsic.base.models import Organization
        model = Organization
        fields =  ("branded_signup_page_header_url", "branded_signup_page_copy", "advertiser_custom_program_page",
                   "advertiser_profile_detail_page")
        layout =  ("branded_signup_page_header_url", "branded_signup_page_copy", "advertiser_custom_program_page",
                   "advertiser_profile_detail_page")
                    
    branded_signup_page_header_url = forms.ImageField(label='Header Image URL', required=False)
    branded_signup_page_copy = forms.CharField(max_length=1024 * 10, label='Branded Signup Page Copy (HTML Preferred)', widget=forms.Textarea,required=False)
    advertiser_custom_program_page = forms.CharField(max_length=1024 * 10, label='Advertiser Custom Program Page', widget=forms.Textarea,required=False)
    advertiser_profile_detail_page = forms.CharField(max_length=1024 * 10, label='Advertiser Profile Detail Page', widget=forms.Textarea,required=False)


class AdvertiserEmailSettingsForm(SmartModelForm):
    pub_program_email = forms.EmailField(required=False, label='Publisher Contact Email')
    non_pub_program_email = forms.EmailField(required=False, label='Non-Publisher Contact Email')

    class Meta:
        from atrinsic.base.models import Organization
        model = Organization
        fields = ('pub_program_email', 'non_pub_program_email')

        
class PublisherEmailSettingsForm(SmartForm):
    pub_program_email = forms.EmailField(required=False, label='Set Preferred Direct Contact Email')


class ProfileRecvForm(SmartModelForm):
    class Meta:
        from atrinsic.base.models import UserProfile
        model = UserProfile
        fields = ('recv_network', 'recv_legal', 'recv_newsletter')


class PublisherProfileRecvForm(SmartModelForm):
    class Meta:
        from atrinsic.base.models import UserProfile
        model = UserProfile
        fields = ('recv_network', 'recv_legal', 'recv_newsletter', 
                 'recv_adv_emails', 'recv_net_newsletter', 'recv_promo_offers')

class AdvertiserSearchForm(SmartForm):
    ''' Search Form
    '''

    class Meta:
        layout = (
            "q", 'date_from', 'date_to', 'vertical', "network_rating"
        )
    
    q = forms.CharField(max_length=256, label='Keyword', required=False)

    date_from = forms.DateField(label='Date Joined', required=False, widget = DateFormattedTextInput)
    date_to= forms.DateField(label='', required=False, widget = DateFormattedTextInput)

    vertical = forms.ChoiceField(label='Category', required=False)
    network_rating = forms.FloatField(label='Rating', required=False)

    #email_marketing = forms.BooleanField(label='Allow Third Party Email Campaigns?',required=False) 

    #direct_linking = forms.BooleanField(label='Allow Direct Linking Through PPC?', required=False) 

    #trademark_bidding = forms.BooleanField(label='Allow Trademark Bidding Through PPC?',required=False)
    def __init__(self, organization, *args, **kwargs):
        from atrinsic.base.models import PublisherVertical
        super(AdvertiserSearchForm, self).__init__(*args, **kwargs)
        choices = [ ( -1, 'Select...'), ]
        choices.extend([ (v.order, v.name) for v in PublisherVertical.objects.filter(is_adult=organization.is_adult).order_by('name') ])
        self.fields['vertical'].choices = choices

class PublisherOrganizationForm(SmartForm):
    ''' Organiztion Settings Form
    '''

    class Meta:
        layout =  ("company_name", "address", "address2",
                     "city", "country", "state", "province", "zipcode")
        


    company_name = forms.CharField(max_length=256, label='Organization Name')

    address = forms.CharField(max_length=256, label='Address')
    address2 = forms.CharField(max_length=256, label='&nbsp;', required=False)
    city = forms.CharField(max_length=256, label='City')
    state = FormStateField(label='State')
    province = FormProvinceField(label='Province', required=False)
    zipcode = forms.CharField(label='Zip/Postal code', required=False)
    country = FormCountryField(label='Country', required=False)
    
    def clean(self):
        clean_data = self.cleaned_data
        if clean_data.get('country', 'US') == 'US':
            try:
                x = int(clean_data.get('zipcode',None))
            except:
                raise forms.ValidationError(u'You must enter a numerical zipcode.')
        elif clean_data.get('country', 'US') == 'CA':
            clean_data['state'] = clean_data['province']
            if not re.match('^[a-zA-Z]{1}[0-9]{1}[a-zA-Z]{1}(\-| |){1}[0-9]{1}[a-zA-Z]{1}[0-9]{1}$', clean_data.get('zipcode','')):
                raise forms.ValidationError(u'You must enter a valid canadian postal code.')
        if clean_data.has_key('province'):
            del clean_data['province']
        return clean_data


class WebsiteForm(SmartModelForm):
    class Meta:
        from atrinsic.base.models import Website
        model = Website
        fields = ('url', 'desc', 'promo_method', 'vertical', 'is_incentive', 'incentive_desc')
        layout =  (
            Fieldset("Website Information",  "url", "desc", "promo_method", "vertical", "is_incentive", "incentive_desc"),
        )

    def clean_incentive_desc(self):
        is_incentive = self.cleaned_data['is_incentive']
        if is_incentive:
            if 'incentive_desc' in self.cleaned_data and \
               len(self.cleaned_data['incentive_desc']):
                return self.cleaned_data['incentive_desc']
            else:
                raise forms.ValidationError('This field is required.')
    def __init__(self, *args, **kwargs):
        from atrinsic.base.models import PublisherVertical
        super(WebsiteForm, self).__init__(*args, **kwargs)
        vc = [('', '------')]
        vc.extend([ (v.order, v.name) for v in PublisherVertical.objects.order_by('name')])
        self.fields['vertical'].choices = vc

 
class ContactInfoForm(SmartModelForm):
    
    class Meta:
        from atrinsic.base.models import OrganizationContacts
        model = OrganizationContacts
    
        fields = ('email', 'phone', 'fax', 'payeename', 'firstname', 'lastname', 'email', 'address', 'address2', 'city',
            'state', 'province', 'zipcode', 'country', 
        )

        layout = (
            Fieldset("Contact Information", "payeename", "firstname", "lastname", "email", "address", "address2", "city", "country", "state", "province", "zipcode", "phone", "fax"),
        )

    province = FormProvinceField(label='* Province', required=False)
    
    def __init__(self, *args, **kwargs):
        super(ContactInfoForm, self).__init__(*args, **kwargs)
        self.fields['payeename'].label = 'Make Check Payable To'
        self.fields['firstname'].label = 'First Name'
        self.fields['lastname'].label = 'Last Name'
        
    def clean(self):
        cleaned_data = self.cleaned_data        
        return cleaned_data  
        
class ContactInfoFormSmall(SmartModelForm):

    class Meta:
        from atrinsic.base.models import OrganizationContacts
        model = OrganizationContacts    	
        #exclude = ('organization','title','ace_contact_id','payeename', 'address', 'address2', 'city', 'state', 'zipcode', 'country',)
        
        fields = ('firstname', 'lastname','email', 'phone', 'fax',)

        layout = ("firstname", "lastname", "email", "phone", "fax",)
    
    def __init__(self, *args, **kwargs):
        super(ContactInfoFormSmall, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['disabled'] = 'disabled'
        self.fields['phone'].widget.attrs['disabled'] = 'disabled'
        
    def clean_phone(self):
        cleaned_data = self.cleaned_data
        phone = self.cleaned_data.get('phone')
        number = phone.replace("-", "")
        '''
        strCountry = self.organization.country
        if strCountry != None:
            if (strCountry.find("US") > -1 or strCountry.find("CA") > -1):
                if number != None and len(number) == 10:
                    return self.cleaned_data['phone']
                else:
                    raise forms.ValidationError(u"Your phone number must be 10 digits long.")            
            else:
                if number != None and len(number) >= 10 and len(number) <= 15:
                    return self.cleaned_data['phone']
                else:
                    raise forms.ValidationError(u"An error has occured. Please try again.")      
        '''
        return number

class ContactInfoFormSmallest(SmartForm):
    xs_firstname = forms.CharField(label='Firstname')
    xs_lastname = forms.CharField(label='Lastname')
    xs_email = forms.EmailField(label='Email')
    
    
class PaymentInfoForm(SmartModelForm):
    
    class Meta:
        from atrinsic.base.models import OrganizationPaymentInfo
        model = OrganizationPaymentInfo
    
        fields = ('currency', 'payment_method', 'paypal_email', 'account_name', 'bank_name', 'routing_number',
            'account_number', 'account_type', 'iban_code', 'tax_classification', 'tax_id', 
        )

        layout = (
            Fieldset("Payment Information", "currency", "payment_method", "paypal_email", ),
            Fieldset("Direct Deposit", "account_name", "bank_name", "account_number","routing_number", "account_type", "iban_code" ),
            Fieldset("Tax Information", "tax_classification", "tax_id",  ),
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        msg = 'This field is required.'
        method = int(cleaned_data.get('payment_method'))
        clean_vars = {
            PAYMENT_CHECK: (
                'payee_name', 'tax_id',
            ),
            PAYMENT_DEPOSIT: (
                'account_name', 'bank_name',
                'routing_number', 'account_number', 'account_type',
            ),
            PAYMENT_PAYPAL: (
                'paypal_email', 'tax_id',
            ),
        }

        vars = clean_vars[method]
        for var in vars:
            data = cleaned_data.get(var, None)
            if data is not None and not len(str(data)):
                self._errors[var] = ErrorList([msg])
                del cleaned_data[var]

        return cleaned_data

class DenyInquiryForm(SmartForm):
    advertiser_reason = forms.ChoiceField(label='Resolve Reason', choices=INQUIRY_DENIAL_REASONS, required=False)
    advertiser_reason_comment = forms.CharField(label="Advertiser Comments",widget=forms.Textarea, required=False)
    '''def clean_advertiser_reason(self):
        return advertiser_reason
        advertiser_reason = self.cleaned_data.get('advertiser_reason',None)
        if advertiser_reason == None:
            raise forms.ValidationError(u"You must select a reason for denying the inquiry")'''
        
            
class OrderInquiryForm(SmartForm):
    advertiser = forms.ChoiceField(label='Advertiser')
    transaction_date = forms.DateField(label="Transaction Date", widget = DateFormattedTextInput)
    order_id = forms.CharField(max_length=256,label='Order ID')
    transaction_amount = forms.FloatField(label='Transaction Amount')
    member_id = forms.CharField(max_length=256,label='Member ID', required=False)
    comments = forms.CharField(max_length=2048, required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        org = kwargs.pop('org')
        super(OrderInquiryForm, self).__init__(*args, **kwargs)
        from atrinsic.base.models import PublisherRelationship
        self.fields['advertiser'].choices = \
                                        ((u.advertiser.id, u.advertiser.name) for u in PublisherRelationship.objects.filter(publisher=org,status=RELATIONSHIP_ACCEPTED))
                                
class PaymentInquiryForm(SmartForm):
    advertiser = forms.ChoiceField(label='Advertiser')
    amount_due = forms.FloatField(label='Amount Due')
    period_beginning = forms.DateField(label='Period Beginning', widget = DateFormattedTextInput)
    period_ending = forms.DateField(label='Period Ending', widget = DateFormattedTextInput)
    comments = forms.CharField(max_length=2048, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        org = kwargs.pop('org')
        super(PaymentInquiryForm, self).__init__(*args, **kwargs)
        from atrinsic.base.models import PublisherRelationship
        self.fields['advertiser'].choices = \
                                        ((u.advertiser.id, u.advertiser.name) for u in PublisherRelationship.objects.filter(publisher=org,status=RELATIONSHIP_ACCEPTED))

'''
class PiggybackForm(SmartForm):
    
    Piggyback pixel update form
    
    class Meta:
        layout = (
            'pixel_url', 
            )
        
    pixel_url = forms.CharField(max_length=1024, label='Piggyback Pixel URL')
'''    
class PiggybackForm(SmartModelForm):
    
    class Meta:
        from atrinsic.base.models import PiggybackPixel
        model = PiggybackPixel
    
        fields = ('advertiser','pixel_type', 'jsinclude', 'content',)
    
    content = forms.CharField(max_length=2048, required=True, widget=forms.Textarea)
    
    def __init__(self, organization, *args, **kwargs):
        super(PiggybackForm, self).__init__(*args, **kwargs)
        from atrinsic.base.models import Organization
        self.fields['jsinclude'].label = 'Javascript Source File'
        self.fields['pixel_type'].widget = forms.widgets.RadioSelect(choices=PIXEL_TYPE_CHOICES)
        self.fields['advertiser'].widget = forms.widgets.Select(choices=[(a.id, a.name) for a in 
        Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_ACCEPTED,status=ORGSTATUS_LIVE,
                    publisher_relationships__publisher=organization).exclude(id = 6).exclude(id = 46).exclude(id = 50)])


class KenshooIntegrationAddForm(SmartModelForm):
    class Meta:
        from atrinsic.base.models import KenshooIntegration
        model = KenshooIntegration
        fields = ('advertiser', 'content',)
    
    content = forms.CharField(max_length=36, required=True, widget=forms.CharField)
    def __init__(self, organization, *args, **kwargs):
        super(KenshooIntegrationAddForm, self).__init__(*args, **kwargs)
        from atrinsic.base.models import Organization
        from atrinsic.base.models import KenshooIntegration
        self.fields['content'].label = 'Kenshoo ID'
        self.fields['advertiser'].widget = forms.widgets.Select(
            choices=[
                (a.id, a.name) for a in 
                Organization.objects.filter(
                    publisher_relationships__status=RELATIONSHIP_ACCEPTED
                    , status=ORGSTATUS_LIVE
                    , publisher_relationships__publisher=organization
                ).extra(
                    where=[' base_organization.id not IN (select advertiser_id from base_kenshoointegration where publisher_id = ' + str(organization.id)+')']
                )
            ]
        )
        self.fields['content'].widget.attrs['size'] = 45

class KenshooIntegrationEditForm(SmartModelForm):
    class Meta:
        from atrinsic.base.models import KenshooIntegration
        model = KenshooIntegration
        fields = ('content',)
    
    content = forms.CharField(max_length=36, required=True, widget=forms.CharField)
    def __init__(self, organization, *args, **kwargs):
        super(KenshooIntegrationEditForm, self).__init__(*args, **kwargs)
        from atrinsic.base.models import Organization
        self.fields['content'].label = 'Kenshoo ID'
        self.fields['content'].widget.attrs['size'] = 45

class W9StatusForm(SmartModelForm):
    class Meta:
        from atrinsic.base.models import W9Status
        model = W9Status
        fields = ('status', 'datereceived',)
        
        layout = (
            Fieldset("W9 Status", "status", "datereceived", ),
        )
        
    def __init__(self, organization, *args, **kwargs):
        super(W9StatusForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget = forms.widgets.Select(choices=W9_STATUS_CHOICES)
        self.fields['datereceived'].label = 'Date Fax Received (MM/DD/YYYY)'

class w9UploadForm(SmartForm):
    ''' Form to Upload W9 Status Form (pdf) '''
    wNineFile = forms.FileField()

class adbuilderForm(SmartForm):
    name = forms.CharField(label='Link Name')
    advertisers = forms.ChoiceField(label='Advertisers')
    websites = forms.ChoiceField(label='Select your website')
    destination = forms.CharField(max_length=256, label='Destination URL')
    content =forms.CharField(label='Link Content', max_length=2048, required=True, widget=forms.Textarea(attrs={'rows': 3,'cols':25 }))
    def __init__(self, organization, *args, **kwargs):
        from atrinsic.base.models import Organization
        super(adbuilderForm, self).__init__(*args, **kwargs)
        from atrinsic.base.models import Website
        self.fields['advertisers'].choices = [(o.id, o.company_name) for o in Organization.objects.filter(publisher_relationships__status=RELATIONSHIP_ACCEPTED,status=ORGSTATUS_LIVE,           publisher_relationships__publisher=organization,adbuilder=True).extra(select={"publisher_id":"select publisher_id from base_organization where id="+str(organization.id)}) ]
        from atrinsic.base.models import Website
        self.fields['websites'].choices = [(w.id, w.url) for w in Website.objects.filter(publisher=organization) ]
    

class BrandForm(SmartForm):
    from django import forms
    class Meta:
        #layout =  (
        #    Fieldset("BrandLock Form", "start_date", "end_date", "campaign"),
        #)
        
        layout =  ("campaigns", "reportType", "xls", "start_date", "end_date","competitors","keyword_groups","keywords","search_provider")
    import datetime
    year = datetime.datetime.now().year
    
    xls = forms.BooleanField(label='Click to Download',required=False)
    start_date = forms.DateField(('%m/%d/%Y'),label='Start Date',required=False,widget = DateFormattedTextInput)
    end_date = forms.DateField(label='End Date',required=False, widget = DateFormattedTextInput)
    campaigns = forms.ChoiceField(label='Campaigns')
    reportType = forms.ChoiceField(label='Report Type',choices=BLR_CHOICES)
    competitors = forms.MultipleChoiceField(label='Competitors')
    keyword_groups = forms.MultipleChoiceField(label='Keyword Group')
    keywords = forms.MultipleChoiceField(label='Keywords')
    search_provider = forms.MultipleChoiceField(label='Search Provider',choices=BLS_PROVIDERS)
    time_period = forms.ChoiceField(label='Time Period',choices=BLR_TIME)
    listing_attributes = forms.MultipleChoiceField(label='Listing Attributes',choices=BLR_LIST_ATT)
    listing_attributes_ratings = forms.MultipleChoiceField(label='Listing Attributes Rating',choices=BLR_LIST_ATT_RAT)
    listing_attributes_reviews = forms.MultipleChoiceField(label='Listing Attributes Reviews',choices=BLR_LIST_ATT_REV)
    listing_section = forms.MultipleChoiceField(label='Listing Section',choices=BLR_LIST_SEC)
    exclude_tracking_urls = forms.ChoiceField(label='Exclude Tracking URL\'s',choices=[('Yes', 'Yes'), ('No', 'No')])
    ad_offer_type = forms.ChoiceField(label='Offer Type',choices=BLR_OFFER_TYPE)
        
    def __init__(self, key, *args, **kwargs):
        from atrinsic.util.aanapi.brandlock.brandlockApi import Brandlock
        from django.utils import simplejson
        
        #Populate Campaigns
        super(BrandForm, self).__init__(*args, **kwargs)
        bl = Brandlock(key)
        choices = bl.list_campaigns(False,True)
        self.fields['campaigns'].choices = choices
        #Populate Competitors
        compChoices = bl.list_competitors(choices[0][0],0)
        self.fields['competitors'].choices = compChoices
        #Populate KeywordGroups
        kwgChoices = bl.list_keyword_groups(choices[0][0],0)
        self.fields['keyword_groups'].choices = kwgChoices
    
    def clean_start_date(self):
        print "FORM VALIDATION ------------"
        print "validating"  + str(self.cleaned_data.get('start_date'))
        
        return self.cleaned_data.get('start_date')


class BrandEditForm(SmartForm):
    from django import forms
                    
    campaigns = forms.ChoiceField(label='Campaigns')
    active = forms.BooleanField(label='Active:',required=True)
    searchp = forms.MultipleChoiceField(label='Search Providers:',choices=BLS_PROVIDERS_EDIT)
    websites = forms.CharField(label='Your Websites', max_length=2048, required=True, widget=forms.Textarea(attrs={'rows': 5,'cols':20 }))
    domains = forms.CharField(label='Destination Domains:', max_length=2048, required=True, widget=forms.Textarea(attrs={'rows': 5,'cols':20 }))
    trademarks = forms.CharField(label='Your TradeMarks:', max_length=2048, required=True, widget=forms.Textarea(attrs={'rows': 5,'cols':20 }))
    
    def __init__(self,key, *args, **kwargs):
        from atrinsic.util.aanapi.brandlock.brandlockApi import Brandlock
        from django.utils import simplejson
        
        super(BrandEditForm, self).__init__(*args, **kwargs)
        bl = Brandlock(key)
        #Campaigns
        choices = bl.list_campaigns(False,True)
        self.fields['campaigns'].choices = choices
        #General Information
        
        
class OrgFilterForm(SmartForm):
    from atrinsic.base.models import Organization

    org_to_add = forms.ModelChoiceField(label='Organization', queryset=Organization.objects.order_by('company_name').extra(where=[' id NOT IN (SELECT organization_id FROM base_organization_filtertypes WHERE filterchoice = 1)' ]))

class ManageOrders(SmartForm):
    orderids = forms.CharField(label='Order ID(s)', widget=forms.Textarea(attrs={'rows': 5, }))
    searchtype = forms.CharField(widget=forms.HiddenInput(),required=False)
    
    searchby = forms.ChoiceField(label='Publishers',widget=forms.widgets.RadioSelect,choices=SRCHPUBORDERSBY_CHOICES)
    searchByPublisher = forms.MultipleChoiceField(label='Select Publishers',required=True )
    orderamtby = forms.ChoiceField(label='Having order amounts', choices=ORDERAMTSBY_CHOICES)
    orderamt = forms.IntegerField(label='$')
    
    start_date = forms.DateField(label='Start Date',required=False, widget = DateFormattedTextInput)
    end_date = forms.DateField(label='End Date',required=False, widget = DateFormattedTextInput)

    def __init__(self, organization, *args, **kwargs):
        super(ManageOrders, self).__init__(*args, **kwargs)
        self.populate_fields(organization)
        
    def populate_fields(self,organization):
        from atrinsic.base.models import Organization
        self.fields['searchByPublisher'].choices.extend([ ('p_%d' % p.id, p.name) for p in Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED, advertiser_relationships__advertiser=organization) ])
        
class CreateOrders(SmartForm):
    publisherid = forms.CharField(label='Publisher ID:', widget=forms.TextInput(attrs={'size':'120'}))
    orderid = forms.CharField(label='Order ID:', widget=forms.TextInput(attrs={'size':'120'}))    
    orderfees = forms.ChoiceField(label='Fees:', widget=forms.widgets.RadioSelect, choices=CREATEORDER_FEES)
    publisherfee = forms.IntegerField(label='Publisher Fee:', widget=forms.TextInput(attrs={'size':'115'}), required=False)
    networkfee = forms.IntegerField(label='Network Fee:', widget=forms.TextInput(attrs={'size':'115'}), required=False)
    orderamt = forms.FloatField(label='Amount', widget=forms.TextInput(attrs={'size':'120'}), required=True)
    order_date = forms.DateField(label='Order Date(MM/DD/YYYY)',required=True, widget = DateFormattedTextInput(format='Y M D',attrs={'size':'120'}))

    def __init__(self, organization, *args, **kwargs):
        super(CreateOrders, self).__init__(*args, **kwargs)
        self.organization = organization
        
        
    def clean_publisherid(self):
        from atrinsic.base.models import Organization
        pid = self.cleaned_data.get('publisherid')
        try:
            if Organization.objects.filter(id = pid).count() == 0:
                raise forms.ValidationError(u"It appears that the PublisherID you entered doesn't exist. Please re-enter and try again.")   
        except:
            raise forms.ValidationError(u"You have entered an invalid PublisherID. Please try again.")    
        print "Check status"        
        if Organization.objects.filter(advertiser_relationships__status=RELATIONSHIP_ACCEPTED, advertiser_relationships__advertiser=self.organization,advertiser_relationships__publisher=pid).count() == 0:
            raise forms.ValidationError(u"The Publisher corresponding to the Publisher ID you are attempting to credit is not in your program. Please double-check the Publisher ID or contact your Atrinsic affiliate manager for assistance.")   
        print "pub is ok"
        return self.cleaned_data.get('publisherid')        
        
    def clean_orderid(self):
        from atrinsic.base.models import Report_OrderDetail, Report_OrderDetail_UpdateLog
        oid = self.cleaned_data.get('orderid')

        if (Report_OrderDetail.objects.filter(order_id = oid).count() > 0) or (Report_OrderDetail_UpdateLog.objects.filter(order_id = oid).count() > 0):
            raise forms.ValidationError(u"The Order ID you are attempting to create already exists.  Please create a new Order ID.")   
        
        return self.cleaned_data.get('orderid')

####################################################################################
############################## Google Analytics Forms ##############################
class GA_ReportForm(SmartModelForm):
    class Meta:
        from atrinsic.base.models import GA_Report
        model = GA_Report
        exclude = ['metric', 'dimension', 'is_active', 'created']
        #exclude = ['dimension', 'is_active', 'created']

        
class GA_AccountForm(SmartModelForm):
    class Meta:
        from atrinsic.base.models import GA_Account
        model = GA_Account

        fields = ('email', 'password', )

        layout = (
            Fieldset("Create User", "email", "password", ) ,          
        )     
    
    def __init__(self, *args, **kwargs):
        super(GA_AccountForm, self).__init__(*args, **kwargs)


####################################################################################