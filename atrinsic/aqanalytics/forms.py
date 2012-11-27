from atrinsic.util.imports import *
from django import forms
from analytics import AqAnalytics
from reports import *
class LoginForm(forms.ModelForm):
    ''' Form to add a Metric to the Quality Scoring System '''
    
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    organization = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        from aqanalytics.models import Users
        model = Users
        fields = ('email', 'password', 'organization')
        
    def clean(self):
        from atrinsic.base.models import Organization
        form_data = self.cleaned_data
        try:
            aa_obj = AqAnalytics(form_data['email'],form_data['password'])
            aa_obj.authenticate()
        except:
            raise forms.ValidationError(u"Login Failed")
        
        form_data['organization'] = Organization.objects.get(pk=form_data['organization'])
        
        return form_data

class ReportForm(forms.Form):
    ''' Form to add a Metric to the Quality Scoring System '''
    
    start_date = forms.DateField(label='Start Date', required=True)
    end_date = forms.DateField(label='End Date', required=True)
    table_id = forms.CharField(widget=forms.HiddenInput())
    sort = forms.CharField(label="Sort", required=False)
    filters = forms.CharField(label="Filters", required=False)
    report_type = forms.ChoiceField(label="Report", choices=REPORT_CHOICES)
    chart_type = forms.ChoiceField(label="Report Layout", choices=CHART_TYPE_CHOICES)
    max_results = forms.CharField(label="Max Results", required=False)
    #metrics = forms.MultipleChoiceField(label='Metrics')
    #dimensions = forms.MultipleChoiceField(label='Dimensions')
    
    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        """for key in metrics:
            for x in metrics[key]:
                self.fields['metrics'].choices.append((x,x))
        for key in dimensions:
            for x in dimensions[key]:
                self.fields['dimensions'].choices.append((x,x))"""
            