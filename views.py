# learning_modules/views.py
from django.shortcuts import render,render_to_response
from django.template import RequestContext
from django.contrib.auth import (authenticate, logout, views)
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.conf import settings
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from learning_modules.models import Module, Section, Activity, Tracker, Media, ModuleDownload
from forms import UploadModuleForm
from uploader import handle_uploaded_file

import os
import shutil
import datetime


def home_view(request):
    module_list = Module.objects.all().order_by('title')
    activity = []
    startdate = datetime.datetime.now()
    staff = User.objects.filter(is_staff=True)
    for i in range(31,-1,-1):
        temp = startdate - datetime.timedelta(days=i)
        day = temp.strftime("%d")
        month = temp.strftime("%m")
        year = temp.strftime("%y")
        count = Tracker.objects.filter(submitted_date__day=day,submitted_date__month=month,submitted_date__year=year).exclude(user_id__in=staff).count()
        activity.append([temp.strftime("%d %b %y"),count])
    return render_to_response('learning_modules/home.html',{'module_list': module_list, 'recent_activity':activity}, context_instance=RequestContext(request))

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
    quiz_activity_digests = Activity.objects.filter(section__in=Section.objects.filter(module=module),type='quiz').values_list('digest',flat=True)
    page_activity_digests = Activity.objects.filter(section__in=Section.objects.filter(module=module),type='page').values_list('digest',flat=True)
    media_digests = Media.objects.filter(module=module).values_list('digest',flat=True)
    dates = []
    startdate = datetime.datetime.now()
    staff = User.objects.filter(is_staff=True)
    for i in range(31,-1,-1):
        temp = startdate - datetime.timedelta(days=i)
        day = temp.strftime("%d")
        month = temp.strftime("%m")
        year = temp.strftime("%y")
        count_act_page = Tracker.objects.filter(digest__in=page_activity_digests,submitted_date__day=day,submitted_date__month=month,submitted_date__year=year).exclude(user_id__in=staff).count()
        count_act_quiz = Tracker.objects.filter(digest__in=quiz_activity_digests,submitted_date__day=day,submitted_date__month=month,submitted_date__year=year).exclude(user_id__in=staff).count()
        count_media = Tracker.objects.filter(digest__in=media_digests,submitted_date__day=day,submitted_date__month=month,submitted_date__year=year).exclude(user_id__in=staff).count()
        dates.append([temp.strftime("%d %b %y"),count_act_page,count_act_quiz,count_media])
    return render_to_response('learning_modules/module-activity.html',{'module': module,'data':dates}, context_instance=RequestContext(request))

def recent_activity_detail(request,id):
    
    try:
        # check only the owner can view 
        if request.user.is_staff:
            module = Module.objects.get(pk=id)
        else:
            module = Module.objects.get(pk=id,user=request.user)
    except Module.DoesNotExist:
        raise Http404
        
    quiz_activity_digests = Activity.objects.filter(section__in=Section.objects.filter(module=module),type='quiz').values_list('digest',flat=True)
    page_activity_digests = Activity.objects.filter(section__in=Section.objects.filter(module=module),type='page').values_list('digest',flat=True)
    media_digests = Media.objects.filter(module=module).values_list('digest',flat=True)
    staff = User.objects.filter(is_staff=True)
    trackers = Tracker.objects.filter(Q(digest__in=quiz_activity_digests)|Q(digest__in=page_activity_digests)|Q(digest__in=media_digests)).exclude(user_id__in=staff).order_by('-submitted_date')
    paginator = Paginator(trackers, 25)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        tracks = paginator.page(page)
        for t in tracks:
            if t.digest in quiz_activity_digests:
                t.title = "Quiz: " + t.get_activity_title(False)
            elif t.digest in page_activity_digests:
                t.title = "Page: " + t.get_activity_title(False)
            elif t.digest in media_digests:
                t.title = "Media: " + t.get_activity_title()
            else:
                t.title = "Unknown"
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)
    return render_to_response('learning_modules/module-activity-detail.html',{'module': module,'page':tracks,}, context_instance=RequestContext(request))