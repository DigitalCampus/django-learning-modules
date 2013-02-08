# learning_modules/views.py
from django.shortcuts import render,render_to_response
from django.template import RequestContext
from django.contrib.auth import (authenticate, logout, views)
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.conf import settings
from learning_modules.models import Module, Section, Activity, Tracker
from forms import UploadModuleForm
from uploader import handle_uploaded_file
import os
import shutil
import datetime


def home_view(request):
    module_list = Module.objects.all().order_by('title')
    return render_to_response('learning_modules/home.html',{'module_list': module_list}, context_instance=RequestContext(request))

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

def recent_activity(request,id):
    module = Module.objects.get(pk=id)
    digests = Activity.objects.filter(section_id__in= Section.objects.filter(module_id=id)).values_list('digest',flat=True)
    dates = []
    startdate = datetime.datetime.now()
    for i in range(31,-1,-1):
        temp = startdate - datetime.timedelta(days=i)
        day = temp.strftime("%d")
        month = temp.strftime("%m")
        year = temp.strftime("%y")
        count = Tracker.objects.filter(digest__in=digests,submitted_date__day=day,submitted_date__month=month,submitted_date__year=year).count()
        dates.append([temp.strftime("%d %b %y"),count])
    return render_to_response('learning_modules/module-activity.html',{'module': module,'data':dates}, context_instance=RequestContext(request))
