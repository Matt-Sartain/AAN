from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models.query import QuerySet
from atrinsic.base.models import Currency
from atrinsic.util.imports import *
from atrinsic.util.tabfunctions import *

# Navigation Tab to View mappings for the Network Account Menu
tabset("Network", 6, "Admin", "network_admin",
       [ ("Network Administration", "network_admin", superadmin_tab),
         ("Currency", "network_admin_currency", superadmin_tab),
         ("Quality Scoring System", "network_admin_scoring", superadmin_tab),
         ])


                                                                                                    
    
@url(r"^admin/(?P<page>[0-9]+)/$", "network_admin")
@url(r"^admin/$", "network_admin")
@tab("Network","Admin","Network Administration")
@superadmin_required
def network_admin(request, page=None):
    ''' View to list and manage the WebRequests'''
    from atrinsic.base.models import WebRequest
    from forms import WebRequestForm
    qs = WebRequest.objects.all()

    if request.method == "POST":
        form = WebRequestForm(request.POST)

        if form.is_valid():
            if form.cleaned_data.get('date_from', None):
                qs = qs.filter(created__gte=form.cleaned_data['date_from'])

            if form.cleaned_data.get('date_to', None):
                qs = qs.filter(created__lte=form.cleaned_data['date_to'])
            
    else:
        form = WebRequestForm()
    
    return object_list(request, queryset=qs.order_by('-created'), allow_empty=True, page=page,
                template_name='network/admin.html', paginate_by=50, extra_context={
                'total_results' : qs.count(),
                'form' : form,
              })

@url(r"^admin/currency/$", "network_admin_currency")
@tab("Network", "Admin", "Currency")
@superadmin_required
def network_admin_currency(request, page=None):
    from atrinsic.base.models import Currency
    return AQ_render_to_response(request, 'network/currency.html', {
                'currencies' : Currency.objects.all().order_by('order'),
            }, context_instance=RequestContext(request))

#@url(r"^admin/currency/edit/$", "network_admin_currency_edit")
@url(r"^admin/currency/edit/(?P<order>\d+)/$", "network_admin_currency_edit")
@tab("Network", "Admin", "Currency")
@superadmin_required
def network_admin_currency_edit(request, order=0):
    ''' Edit a Currency Exchange Rate '''
    from atrinsic.base.models import Currency
    from forms import ExchangeRateForm
    
    if request.POST:
        form = ExchangeRateForm(request.POST)

        if form.is_valid():
            try:
                er = Currency.objects.get(name=form.cleaned_data['name']) #Check for ToUpper.
                er.rate = str(form.cleaned_data['rate'])
                er.save()

            except Currency.DoesNotExist:
                Currency.objects.create(name=form.cleaned_data['name'], rate=str(form.cleaned_data['rate']))

            return HttpResponseRedirect('/network/admin/currency/')

    else:
    	c = Currency.objects.get(order=order)
        form = ExchangeRateForm(initial={ 
                        'name' : c.name,
                        'rate' : c.rate,
                    })

    return AQ_render_to_response(request, 'network/currency-edit.html', {
                'form' : form,
                'order': order,
            }, context_instance=RequestContext(request))

@url(r"^admin/scoring/$", "network_admin_scoring")
@tab("Network","Admin","Quality Scoring System")
@superadmin_required
def network_admin_scoring(request):
    ''' View to list and manage the the Publisher Quality Scoring System'''
    from atrinsic.base.models import QualityScoringSystemMetric
    from forms import QualityScoringSystemMetricForm
    metrics = QualityScoringSystemMetric.objects.all().order_by('key')

    if request.method == 'POST':
        form = QualityScoringSystemMetricForm(request.POST) 

        if form.is_valid():
            QualityScoringSystemMetric.objects.create(key=form.cleaned_data['key'], weight=str(form.cleaned_data['weight']))

            return HttpResponseRedirect('/network/admin/scoring/')
    else:
        form = QualityScoringSystemMetricForm() 

    return AQ_render_to_response(request, 'network/scoring.html', {
                'form' : form,
                'metrics' : metrics,
            }, context_instance=RequestContext(request))


@url(r"^admin/scoring/(?P<id>[0-9]+)/$", "network_admin_scoring_delete")
@tab("Network","Admin","Quality Scoring System")
@superadmin_required
def network_admin_scoring_delete(request, id):
    ''' View to delete a metric from the Quality Scoring System '''
    from atrinsic.base.models import QualityScoringSystemMetric
    m = get_object_or_404(QualityScoringSystemMetric, id=id)

    m.delete()

    return HttpResponseRedirect('/network/admin/scoring/')

