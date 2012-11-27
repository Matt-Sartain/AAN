import os
from django import forms
from django.template import Context,RequestContext
from django.template.loader import get_template, select_template
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.forms.forms import BoundField
from django.utils.html import escape
from django.forms.fields import Field
from django.forms.forms import get_declared_fields
from django.forms.widgets import media_property
from django.forms.models import BaseModelForm, fields_for_model, \
                                ModelFormMetaclass, ModelFormOptions
from django.forms.forms import BaseForm, DeclarativeFieldsMetaclass


#from atrinsic.util.AceFieldLists import *

class NoSuchFormField(Exception):
    "The form field couldn't be resolved."
    pass


def error_list(errors):
    return '<ul class="errors"><li>' + \
           '</li><li>'.join(errors) + \
           '</li></ul>'


class SortedDictFromList(SortedDict):
    "A dictionary that keeps its keys in the order in which they're inserted."
    # This is different than django.utils.datastructures.SortedDict, because
    # this takes a list/tuple as the argument to __init__().
    def __init__(self, data=None):
        if data is None: data = []
        self.keyOrder = [d[0] for d in data]
        dict.__init__(self, dict(data))

    def copy(self):
        return SortedDictFromList([(k, copy.copy(v)) for k, v in self.items()])


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, Field)]
        fields.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))

        # If this class is subclassing another Form, add that Form's fields.
        # Note that we loop over the bases in *reverse*. This is necessary in
        # order to preserve the correct order of fields.
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                fields = base.base_fields.items() + fields

        attrs['base_fields'] = SortedDictFromList(fields)


        return type.__new__(cls, name, bases, attrs)


class SmartModelFormMetaclass(type):
    def __new__(cls, name, bases, attrs):
        fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, Field)]
        fields.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))

        # If this class is subclassing another Form, add that Form's fields.
        # Note that we loop over the bases in *reverse*. This is necessary in
        # order to preserve the correct order of fields.
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                fields = base.base_fields.items() + fields

        attrs['base_fields'] = SortedDictFromList(fields)

        # rest of this method is taken from actual django 
        # source for ModelFormMetaclass class
        formfield_callback = attrs.pop('formfield_callback',
                lambda f: f.formfield())
        try:
            parents = [b for b in bases if issubclass(b, BaseModelForm)]
        except NameError:
            # We are defining ModelForm itself.
            parents = None
        declared_fields = get_declared_fields(bases, attrs, False)
        new_class = super(SmartModelFormMetaclass, cls).__new__(cls, name, bases,
                attrs)
        if not parents:
            return new_class

        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        opts = new_class._meta = ModelFormOptions(getattr(new_class, 'Meta', None))
        if opts.model:
            # If a model is defined, extract form fields from it.
            fields = fields_for_model(opts.model, opts.fields,
                                      opts.exclude, formfield_callback)
            # Override default model fields with any custom declared ones
            # (plus, include all the other declared fields).
            fields.update(declared_fields)
        else:
            fields = declared_fields
        new_class.declared_fields = declared_fields
        new_class.base_fields = fields
        return new_class


class BaseSmartForm(BaseForm):    
    def __init__(self, *args, **kwargs):

        super(BaseSmartForm, self).__init__(*args,**kwargs)

        # do we have an explicit layout?

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'layout'):
            self.layout = self.Meta.layout
        else:
            # Construct a simple layout using the keys from the fields
            self.layout = self.fields.keys()

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'custom_fields'):
            self.custom_fields = self.Meta.custom_fields
        else:
            self.custom_fields = {}

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'template_base'):
            self.template_base = self.Meta.template_base
        else:
            self.template_base = "smartforms"

        self.prefix = []
        self.top_errors = []

    def as_div(self):
        ''' Render the form as a set of <div>s. '''

        output = self.render_fields(self.layout)
        prefix = u''.join(self.prefix)

        self.top_errors.extend(self.non_field_errors())
        
        if self.top_errors:
            errors = error_list(self.top_errors)
        else:
            errors = u''

        self.prefix = []
        self.top_errors = []

        return mark_safe(prefix + errors + output)

    def as_dictionary(self):
        output = {}
        for field in self.fields.keys():            
            bf = BoundField(self, self.fields[field], field)
            if not self.is_bound:
                data = self.initial.get(bf.name, bf.field.initial)
                if callable(data):
                    data = data()
            else:
                data = bf.data
            output[field] = data
        return output
    
    # Default output is now as <div> tags.
    
    __str__ = as_div
    __unicode__ = as_div

    def render_fields(self, fields, separator=u""):

        ''' Render a list of fields and join the fields by
            the value in separator. '''

        output = []
        
        for field in fields:

            if isinstance(field, (Columns, Fieldset, HTML)):
                output.append(field.as_html(self))
            else:
                output.append(self.render_field(field))

        return separator.join(output)

    def render_field(self, field):

        ''' Render a named field to HTML. '''

        try:
            field_instance = self.fields[field]
        except KeyError:
            raise NoSuchFormField("Could not resolve form field '%s'." % field)

        bf = BoundField(self, field_instance, field)

        output = ''

        bf_errors = self.error_class([escape(error) for error in bf.errors])

        if bf.is_hidden:

            # If the field is hidden, add it at the top of the form

            self.prefix.append(unicode(bf))

            # If the hidden field has errors, append them to the top_errors
            # list which will be printed out at the top of form
            
            if bf_errors:
                self.top_errors.extend(bf.errors)

        else:

            # Find field + widget type css classes
            css_class = type(field_instance).__name__ + " " + \
                        type(field_instance.widget).__name__

            # Add an extra class, Required, if applicable
            if field_instance.required:
                css_class += " Required"

            if field_instance.help_text:
                # The field has a help_text, construct <span> tag
                help_text = escape(field_instance.help_text)
                help_text = '<span class="help_text">%s</span>' % help_text

            else:
                help_text = u''

            field_hash = {'field':mark_safe(field),
                          'class':mark_safe(css_class),
                          'label':mark_safe(bf.label and bf.label_tag(bf.label) or ''),
                          'help_text':mark_safe(help_text),
                          'field':field_instance,
                          'bf':mark_safe(unicode(bf)),
                          'bf_raw':bf,
                          'errors':mark_safe(bf_errors),
                          'field_type':mark_safe(field.__class__.__name__)}
            
            if self.custom_fields.has_key(field):
                template = get_template(self.custom_fields[field])
            else:
                template = select_template([
                    os.path.join(self.template_base,'field_%s.html' % field_instance.__class__.__name__.lower()),
                    os.path.join(self.template_base,'field_default.html')]
                                           )
                
            # Finally render the field
            output = template.render(Context(field_hash))

            # output = '<div class="field %(class)s">%(label)s%(help_text)s%(errors)s<div class="input">%(field)s</div></div>\n' % {'class': css_class, 'label': label, 'help_text': help_text, 'errors': bf_errors, 'field': unicode(bf)}

        return mark_safe(output)


class SmartForm(BaseSmartForm):
    __metaclass__ = DeclarativeFieldsMetaclass


class BaseSmartModelForm(BaseModelForm):
    def __init__(self, *args, **kwargs):

        super(BaseSmartModelForm, self).__init__(*args,**kwargs)

        # do we have an explicit layout?

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'layout'):
            self.layout = self.Meta.layout
        else:
            # Construct a simple layout using the keys from the fields
            self.layout = self.fields.keys()

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'custom_fields'):
            self.custom_fields = self.Meta.custom_fields
        else:
            self.custom_fields = {}

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'template_base'):
            self.template_base = self.Meta.template_base
        else:
            self.template_base = "smartforms"

        self.prefix_r = []
        self.top_errors = []

    def as_div(self):
        ''' Render the form as a set of <div>s. '''

        output = self.render_fields(self.layout)
        prefix_r = u''.join(self.prefix_r)

        self.top_errors.extend(self.non_field_errors())

        if self.top_errors:
            errors = error_list(self.top_errors)
        else:
            errors = u''

        self.prefix_r = []
        self.top_errors = []

        return mark_safe(prefix_r + errors + output)

    # Default output is now as <div> tags.

    __str__ = as_div
    __unicode__ = as_div

    def render_fields(self, fields, separator=u""):

        ''' Render a list of fields and join the fields by
            the value in separator. '''
        output = []

        for field in fields:

            if isinstance(field, (Columns, Fieldset, HTML)):
                output.append(field.as_html(self))
            else:
                output.append(self.render_field(field))

        return separator.join(output)

    def render_field(self, field):

        ''' Render a named field to HTML. '''

        try:
            field_instance = self.fields[field]
        except KeyError:
            raise NoSuchFormField("Could not resolve form field '%s'." % field)

        bf = BoundField(self, field_instance, field)

        output = ''

        bf_errors = self.error_class([escape(error) for error in bf.errors])

        if bf.is_hidden:

            # If the field is hidden, add it at the top of the form

            self.prefix_r.append(unicode(bf))

            # If the hidden field has errors, append them to the top_errors
            # list which will be printed out at the top of form

            if bf_errors:
                self.top_errors.extend(bf.errors)
        else:

            # Find field + widget type css classes
            css_class = type(field_instance).__name__ + " " + \
                        type(field_instance.widget).__name__

            # Add an extra class, Required, if applicable
            if field_instance.required:
                css_class += " Required"

            if field_instance.help_text:
                # The field has a help_text, construct <span> tag
                help_text = escape(field_instance.help_text)
                help_text = '<span class="help_text">%s</span>' % help_text

            else:
                help_text = u''

            field_hash = {'field':mark_safe(field),
                          'class':mark_safe(css_class),
                          'label':mark_safe(bf.label and bf.label_tag(bf.label) or ''),
                          'help_text':mark_safe(help_text),
                          'field':field_instance,
                          'bf':mark_safe(unicode(bf)),
                          'bf_raw':bf,
                          'errors':mark_safe(bf_errors),
                          'field_type':mark_safe(field.__class__.__name__)}

            if self.custom_fields.has_key(field):
                template = get_template(self.custom_fields[field])
            else:
                template = select_template([
                    os.path.join(self.template_base,'field_%s.html' % field_instance.__class__.__name__.lower()),
                    os.path.join(self.template_base,'field_default.html')]
                                           )

            # Finally render the field
            output = template.render(Context(field_hash))

        return mark_safe(output)


class SmartModelForm(BaseSmartModelForm):
    #__metaclass__ = DeclarativeFieldsMetaclass
    __metaclass__ = SmartModelFormMetaclass


class Fieldset(object):

    ''' Fieldset container. Renders to a <fieldset>. '''

    def __init__(self, legend, *fields):
        self.legend_html = legend and ('<legend>%s</legend>' % legend) or ''
        self.fields = fields
    
    def as_html(self, form):
        return u'<fieldset>%s%s</fieldset>' % \
               (self.legend_html, form.render_fields(self.fields))
            
class Columns(object):
    ''' Columns container. Renders to a set og <div>s named
        with classes as used by YUI (Yahoo UI)  '''

    def __init__(self, *columns, **kwargs):
        self.columns = columns
        self.css_class = kwargs.has_key('css_class') and kwargs['css_class'] or 'yui-g'

    def as_html(self, form):
        output = []
        first = " first"

        output.append('<div class="%s">' % self.css_class)

        for fields in self.columns:
            output.append('<div class="yui-u%s">%s</div>' % \
                          (first, form.render_fields(fields)))
            first = ''

        output.append('</div>')

        return u''.join(output)

class HTML(object):

    ''' HTML container '''

    def __init__(self, html):
        self.html = html

    def as_html(self, form):
        return self.html
        
from django.utils.translation import ugettext as _
from django.db import models
# ISO 3166-1 country names and codes adapted from http://opencountrycodes.appspot.com/python/
COUNTRIES = (
    ('AF', _('Afghanistan')), 
    ('AX', _('Aland Islands')), 
    ('AL', _('Albania')), 
    ('DZ', _('Algeria')), 
    ('AS', _('American Samoa')), 
    ('AD', _('Andorra')), 
    ('AO', _('Angola')), 
    ('AI', _('Anguilla')), 
    ('AQ', _('Antarctica')), 
    ('AG', _('Antigua and Barbuda')), 
    ('AR', _('Argentina')), 
    ('AM', _('Armenia')), 
    ('AW', _('Aruba')), 
    ('AU', _('Australia')), 
    ('AT', _('Austria')), 
    ('AZ', _('Azerbaijan')), 
    ('BS', _('Bahamas')), 
    ('BH', _('Bahrain')), 
    ('BD', _('Bangladesh')), 
    ('BB', _('Barbados')), 
    ('BY', _('Belarus')), 
    ('BE', _('Belgium')), 
    ('BZ', _('Belize')), 
    ('BJ', _('Benin')), 
    ('BM', _('Bermuda')), 
    ('BT', _('Bhutan')), 
    ('BO', _('Bolivia')), 
    ('BA', _('Bosnia and Herzegovina')), 
    ('BW', _('Botswana')), 
    ('BV', _('Bouvet Island')), 
    ('BR', _('Brazil')), 
    ('IO', _('British Indian Ocean Territory')), 
    ('BN', _('Brunei Darussalam')), 
    ('BG', _('Bulgaria')), 
    ('BF', _('Burkina Faso')), 
    ('BI', _('Burundi')), 
    ('KH', _('Cambodia')), 
    ('CM', _('Cameroon')), 
    ('CA', _('Canada')), 
    ('CV', _('Cape Verde')), 
    ('KY', _('Cayman Islands')), 
    ('CF', _('Central African Republic')), 
    ('TD', _('Chad')), 
    ('CL', _('Chile')), 
    ('CN', _('China')), 
    ('CX', _('Christmas Island')), 
    ('CC', _('Cocos (Keeling) Islands')), 
    ('CO', _('Colombia')), 
    ('KM', _('Comoros')), 
    ('CG', _('Congo')), 
    ('CD', _('Congo, The Democratic Republic of the')), 
    ('CK', _('Cook Islands')), 
    ('CR', _('Costa Rica')), 
    ('CI', _('Cote d\'Ivoire')), 
    ('HR', _('Croatia')), 
    ('CU', _('Cuba')), 
    ('CY', _('Cyprus')), 
    ('CZ', _('Czech Republic')), 
    ('DK', _('Denmark')), 
    ('DJ', _('Djibouti')), 
    ('DM', _('Dominica')), 
    ('DO', _('Dominican Republic')), 
    ('EC', _('Ecuador')), 
    ('EG', _('Egypt')), 
    ('SV', _('El Salvador')), 
    ('GQ', _('Equatorial Guinea')), 
    ('ER', _('Eritrea')), 
    ('EE', _('Estonia')), 
    ('ET', _('Ethiopia')), 
    ('FK', _('Falkland Islands (Malvinas)')), 
    ('FO', _('Faroe Islands')), 
    ('FJ', _('Fiji')), 
    ('FI', _('Finland')), 
    ('FR', _('France')), 
    ('GF', _('French Guiana')), 
    ('PF', _('French Polynesia')), 
    ('TF', _('French Southern Territories')), 
    ('GA', _('Gabon')), 
    ('GM', _('Gambia')), 
    ('GE', _('Georgia')), 
    ('DE', _('Germany')), 
    ('GH', _('Ghana')), 
    ('GI', _('Gibraltar')), 
    ('GR', _('Greece')), 
    ('GL', _('Greenland')), 
    ('GD', _('Grenada')), 
    ('GP', _('Guadeloupe')), 
    ('GU', _('Guam')), 
    ('GT', _('Guatemala')), 
    ('GG', _('Guernsey')), 
    ('GN', _('Guinea')), 
    ('GW', _('Guinea-Bissau')), 
    ('GY', _('Guyana')), 
    ('HT', _('Haiti')), 
    ('HM', _('Heard Island and McDonald Islands')), 
    ('VA', _('Holy See (Vatican City State)')), 
    ('HN', _('Honduras')), 
    ('HK', _('Hong Kong')), 
    ('HU', _('Hungary')), 
    ('IS', _('Iceland')), 
    ('IN', _('India')), 
    ('ID', _('Indonesia')), 
    ('IR', _('Iran, Islamic Republic of')), 
    ('IQ', _('Iraq')), 
    ('IE', _('Ireland')), 
    ('IM', _('Isle of Man')), 
    ('IL', _('Israel')), 
    ('IT', _('Italy')), 
    ('JM', _('Jamaica')), 
    ('JP', _('Japan')), 
    ('JE', _('Jersey')), 
    ('JO', _('Jordan')), 
    ('KZ', _('Kazakhstan')), 
    ('KE', _('Kenya')), 
    ('KI', _('Kiribati')), 
    ('KP', _('Korea, Democratic People\'s Republic of')), 
    ('KR', _('Korea, Republic of')), 
    ('KW', _('Kuwait')), 
    ('KG', _('Kyrgyzstan')), 
    ('LA', _('Lao People\'s Democratic Republic')), 
    ('LV', _('Latvia')), 
    ('LB', _('Lebanon')), 
    ('LS', _('Lesotho')), 
    ('LR', _('Liberia')), 
    ('LY', _('Libyan Arab Jamahiriya')), 
    ('LI', _('Liechtenstein')), 
    ('LT', _('Lithuania')), 
    ('LU', _('Luxembourg')), 
    ('MO', _('Macao')), 
    ('MK', _('Macedonia, The Former Yugoslav Republic of')), 
    ('MG', _('Madagascar')), 
    ('MW', _('Malawi')), 
    ('MY', _('Malaysia')), 
    ('MV', _('Maldives')), 
    ('ML', _('Mali')), 
    ('MT', _('Malta')), 
    ('MH', _('Marshall Islands')), 
    ('MQ', _('Martinique')), 
    ('MR', _('Mauritania')), 
    ('MU', _('Mauritius')), 
    ('YT', _('Mayotte')), 
    ('MX', _('Mexico')), 
    ('FM', _('Micronesia, Federated States of')), 
    ('MD', _('Moldova')), 
    ('MC', _('Monaco')), 
    ('MN', _('Mongolia')), 
    ('ME', _('Montenegro')), 
    ('MS', _('Montserrat')), 
    ('MA', _('Morocco')), 
    ('MZ', _('Mozambique')), 
    ('MM', _('Myanmar')), 
    ('NA', _('Namibia')), 
    ('NR', _('Nauru')), 
    ('NP', _('Nepal')), 
    ('NL', _('Netherlands')), 
    ('AN', _('Netherlands Antilles')), 
    ('NC', _('New Caledonia')), 
    ('NZ', _('New Zealand')), 
    ('NI', _('Nicaragua')), 
    ('NE', _('Niger')), 
    ('NG', _('Nigeria')), 
    ('NU', _('Niue')), 
    ('NF', _('Norfolk Island')), 
    ('MP', _('Northern Mariana Islands')), 
    ('NO', _('Norway')), 
    ('OM', _('Oman')), 
    ('PK', _('Pakistan')), 
    ('PW', _('Palau')), 
    ('PS', _('Palestinian Territory, Occupied')), 
    ('PA', _('Panama')), 
    ('PG', _('Papua New Guinea')), 
    ('PY', _('Paraguay')), 
    ('PE', _('Peru')), 
    ('PH', _('Philippines')), 
    ('PN', _('Pitcairn')), 
    ('PL', _('Poland')), 
    ('PT', _('Portugal')), 
    ('PR', _('Puerto Rico')), 
    ('QA', _('Qatar')), 
    ('RE', _('Reunion')), 
    ('RO', _('Romania')), 
    ('RU', _('Russian Federation')), 
    ('RW', _('Rwanda')), 
    ('BL', _('Saint Barthelemy')), 
    ('SH', _('Saint Helena')), 
    ('KN', _('Saint Kitts and Nevis')), 
    ('LC', _('Saint Lucia')), 
    ('MF', _('Saint Martin')), 
    ('PM', _('Saint Pierre and Miquelon')), 
    ('VC', _('Saint Vincent and the Grenadines')), 
    ('WS', _('Samoa')), 
    ('SM', _('San Marino')), 
    ('ST', _('Sao Tome and Principe')), 
    ('SA', _('Saudi Arabia')), 
    ('SN', _('Senegal')), 
    ('RS', _('Serbia')), 
    ('SC', _('Seychelles')), 
    ('SL', _('Sierra Leone')), 
    ('SG', _('Singapore')), 
    ('SK', _('Slovakia')), 
    ('SI', _('Slovenia')), 
    ('SB', _('Solomon Islands')), 
    ('SO', _('Somalia')), 
    ('ZA', _('South Africa')), 
    ('GS', _('South Georgia and the South Sandwich Islands')), 
    ('ES', _('Spain')), 
    ('LK', _('Sri Lanka')), 
    ('SD', _('Sudan')), 
    ('SR', _('Suriname')), 
    ('SJ', _('Svalbard and Jan Mayen')), 
    ('SZ', _('Swaziland')), 
    ('SE', _('Sweden')), 
    ('CH', _('Switzerland')), 
    ('SY', _('Syrian Arab Republic')), 
    ('TW', _('Taiwan, Province of China')), 
    ('TJ', _('Tajikistan')), 
    ('TZ', _('Tanzania, United Republic of')), 
    ('TH', _('Thailand')), 
    ('TL', _('Timor-Leste')), 
    ('TG', _('Togo')), 
    ('TK', _('Tokelau')), 
    ('TO', _('Tonga')), 
    ('TT', _('Trinidad and Tobago')), 
    ('TN', _('Tunisia')), 
    ('TR', _('Turkey')), 
    ('TM', _('Turkmenistan')), 
    ('TC', _('Turks and Caicos Islands')), 
    ('TV', _('Tuvalu')), 
    ('UG', _('Uganda')), 
    ('UA', _('Ukraine')), 
    ('AE', _('United Arab Emirates')), 
    ('GB', _('United Kingdom')), 
    ('US', _('United States')), 
    ('UM', _('United States Minor Outlying Islands')), 
    ('UY', _('Uruguay')), 
    ('UZ', _('Uzbekistan')), 
    ('VU', _('Vanuatu')), 
    ('VE', _('Venezuela')), 
    ('VN', _('Viet Nam')), 
    ('VG', _('Virgin Islands, British')), 
    ('VI', _('Virgin Islands, U.S.')), 
    ('WF', _('Wallis and Futuna')), 
    ('EH', _('Western Sahara')), 
    ('YE', _('Yemen')), 
    ('ZM', _('Zambia')), 
    ('ZW', _('Zimbabwe')), 
)

COUNTRIES_PARTIAL = (
    ('CA', _('Canada')), 
    ('US', _('United States')), 
    ('CN', _('China')), 
)
class CountryField(models.CharField):
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 2)
        kwargs.setdefault('choices', COUNTRIES)

        super(CountryField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

class FormCountryField(forms.ChoiceField):
    
    def __init__(self, partial=False, *args, **kwargs):
        if partial:
            kwargs.setdefault('choices', COUNTRIES_PARTIAL)
        else:
            kwargs.setdefault('choices', COUNTRIES)

        super(FormCountryField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "ChoiceField"
STATES = (
    ('AK', _('Alaska')),
    ('AL', _('Alabama')),
    ('AR', _('Arkansas')),
    ('AZ', _('Arizona')),
    ('CA', _('California')),
    ('CO', _('Colorado')),
    ('CT', _('Connecticut')),
    ('DE', _('Delaware')),
    ('FL', _('Florida')),
    ('GA', _('Georgia')),
    ('HI', _('Hawaii')),
    ('IA', _('Iowa')),
    ('ID', _('Idaho')),
    ('IL', _('Illinois')),
    ('IN', _('Indiana')),
    ('KS', _('Kansas')),
    ('KY', _('Kentucky')),
    ('LA', _('Louisiana')),
    ('MA', _('Massachusetts')),
    ('MD', _('Maryland')),
    ('ME', _('Maine')),
    ('MI', _('Michigan')),
    ('MN', _('Minnesota')),
    ('MO', _('Missouri')),
    ('MS', _('Mississippi')),
    ('MT', _('Montana')),
    ('NC', _('North Carolina')),
    ('ND', _('North Dakota')),
    ('NE', _('Nebraska')),
    ('NH', _('New Hampshire')),
    ('NJ', _('New Jersey')),
    ('NM', _('New Mexico')),
    ('NV', _('Nevada')),
    ('NY', _('New York')),
    ('OH', _('Ohio')),
    ('OK', _('Oklahoma')),
    ('OR', _('Oregon')),
    ('PA', _('Pennsylvania')),
    ('RI', _('Rhode Island')),
    ('SC', _('South Carolina')),
    ('SD', _('South Dakota')),
    ('TN', _('Tennessee')),
    ('TX', _('Texas')),
    ('UT', _('Utah')),
    ('VT', _('Vermont')),
    ('VA', _('Virginia')),
    ('WA', _('Washington')),
    ('DC', _('Washington DC')),
    ('WI', _('Wisconsin')),
    ('WV', _('West Virginia')),
    ('WY', _('Wyoming')),
)
PROVINCES = (
    ('AB', _('Alberta')),
    ('BC', _('British Columbia')),
    ('MB', _('Manitoba')),
    ('NB', _('New-Brunswick')),
    ('NL', _('Newfoundland and Labrador')),
    ('NS', _('Nova-Scotia')),
    ('NT', _('Northwest Territories')),
    ('NU', _('Nunavut')),
    ('ON', _('Ontario')),
    ('PE', _('Prince Edward Island')),
    ('QC', _('Quebec')),
    ('SK', _('Saskatchewan')),
    ('YT', _('Yukon')),
)
class ProvinceField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 2)
        kwargs.setdefault('choices', PROVINCES)

        super(ProvinceField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

class FormProvinceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', PROVINCES)

        super(FormProvinceField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "ChoiceField"
        
class StateField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 2)
        kwargs.setdefault('choices', STATES)

        super(StateField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

class FormStateField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', STATES)

        super(FormStateField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "ChoiceField"
