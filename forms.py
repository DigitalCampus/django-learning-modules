from django import forms

class UploadModuleForm(forms.Form):
    module_file = forms.FileField()
    