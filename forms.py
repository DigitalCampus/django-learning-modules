from django import forms
from django.contrib.admin import widgets
from learning_modules.models import Schedule

class UploadModuleForm(forms.Form):
    module_file = forms.FileField()
    

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ('title', 'default')
        widgets = {
            'title': forms.TextInput(attrs={'size':'60'}),     
        }
        
class ActivityScheduleForm(forms.Form):
    title = forms.CharField(widget=forms.HiddenInput())
    digest =  forms.CharField(widget=forms.HiddenInput())
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)
    section = forms.CharField(widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = super(ActivityScheduleForm, self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date is None and end_date is not None:
            raise forms.ValidationError("You must enter both a start and end date.")

        if start_date is not None and end_date is None:
            raise forms.ValidationError("You must enter both a start and end date.")
        
        if start_date > end_date:
            raise forms.ValidationError("Start date must be before the end date.")

        return cleaned_data
    