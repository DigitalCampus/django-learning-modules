# learning_modules/views.py
from django.shortcuts import render,render_to_response
from django.template import RequestContext
from django.contrib.auth import (authenticate, logout, views)
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.conf import settings
from mquiz.models import Quiz
from forms import UploadModuleForm
from uploader import handle_uploaded_file
import os
import shutil

def home_view(request):
    latest_quiz_list = Quiz.objects.filter(draft=0).order_by('-created_date')[:10]
    return render_to_response('learning_modules/home.html',{'latest_quiz_list': latest_quiz_list}, context_instance=RequestContext(request))

def upload(request):
    if request.method == 'POST': # if form submitted...
        form = UploadModuleForm(request.POST,request.FILES)
        if form.is_valid(): # All validation rules pass
            extract_path = settings.MODULE_UPLOAD_DIR + 'temp/' + str(request.user.id) + '/' 
            if handle_uploaded_file(request.FILES['module_file'], extract_path, request):
                shutil.rmtree(extract_path)
                return HttpResponseRedirect('success/') # Redirect after POST
            else:
                shutil.rmtree(extract_path,ignore_errors=True)
                os.remove(settings.MODULE_UPLOAD_DIR + request.FILES['module_file'].name)
    else:
        form = UploadModuleForm() # An unbound form

    return render(request, 'learning_modules/upload.html', {'form': form,})