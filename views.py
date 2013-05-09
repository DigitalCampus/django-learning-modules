# learning_modules/views.py
from django.shortcuts import render,render_to_response
from django.template import RequestContext
from django.contrib.auth import (authenticate, logout, views)
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.conf import settings
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from learning_modules.models import Module, Section, Activity, Tracker, Media, ModuleDownload, Schedule, ActivitySchedule, Cohort, Participant
from forms import UploadModuleForm, ScheduleForm, ActivityScheduleForm
from django import forms
from django.forms.formsets import formset_factory
from uploader import handle_uploaded_file

import os
import shutil
import datetime
  
def home_view(request):
    module_list = Module.objects.all().order_by('title')
    module_set = []
    for m in module_list:
        m.activity = []
        module_set.append(m)
    activity = []
    startdate = datetime.datetime.now()
    staff = User.objects.filter(is_staff=True)
    for i in range(31,-1,-1):
        temp = startdate - datetime.timedelta(days=i)
        day = temp.strftime("%d")
        month = temp.strftime("%m")
        year = temp.strftime("%y")
        count = Tracker.objects.filter(tracker_date__day=day,tracker_date__month=month,tracker_date__year=year).exclude(user_id__in=staff).count()
        activity.append([temp.strftime("%d %b %y"),count])
        for m in module_set:
            mod_count = Tracker.objects.filter(module=m, tracker_date__day=day,tracker_date__month=month,tracker_date__year=year).exclude(user_id__in=staff).count()
            m.activity.append([temp.strftime("%d %b %y"),mod_count])
    return render_to_response('learning_modules/home.html',{'module_set': module_set, 'recent_activity':activity}, context_instance=RequestContext(request))

def upload(request):
    if request.method == 'POST':
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
    dates = []
    startdate = datetime.datetime.now()
    staff = User.objects.filter(is_staff=True)
    for i in range(31,-1,-1):
        temp = startdate - datetime.timedelta(days=i)
        day = temp.strftime("%d")
        month = temp.strftime("%m")
        year = temp.strftime("%y")
        count_act_page = Tracker.objects.filter(module=module,type='page',tracker_date__day=day,tracker_date__month=month,tracker_date__year=year).exclude(user_id__in=staff).count()
        count_act_quiz = Tracker.objects.filter(module=module,type='quiz',tracker_date__day=day,tracker_date__month=month,tracker_date__year=year).exclude(user_id__in=staff).count()
        count_media = Tracker.objects.filter(module=module,type='media',tracker_date__day=day,tracker_date__month=month,tracker_date__year=year).exclude(user_id__in=staff).count()
        dates.append([temp.strftime("%d %b %y"),count_act_page,count_act_quiz,count_media])
    return render_to_response('learning_modules/module-activity.html',{'module': module,'data':dates}, context_instance=RequestContext(request))

def recent_activity_detail(request,id):
    module = check_owner(request,id)
        
    staff = User.objects.filter(is_staff=True)
    trackers = Tracker.objects.filter(module=module).exclude(user_id__in=staff).order_by('-tracker_date')
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
            t.title = t.get_activity_title()
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)
    return render_to_response('learning_modules/module-activity-detail.html',{'module': module,'page':tracks,}, context_instance=RequestContext(request))


def schedule(request,id):
    module = check_owner(request,id)    
    return render_to_response('learning_modules/module-schedules.html',{'module': module,'default_schedule':module.get_default_schedule(),'cohort_schedules':None}, context_instance=RequestContext(request))
    
def schedule_add(request,id):
    module = check_owner(request,id)
    ActivityScheduleFormSet = formset_factory(ActivityScheduleForm, extra=0)
    activities = Activity.objects.filter(section__module = module)
    initial = []
    section = None
    start_date = datetime.datetime.now() 
    end_date = datetime.datetime.now() + datetime.timedelta(days=7)
    for a in activities:
        if a.section != section:
            section = a.section
            start_date = start_date + datetime.timedelta(days=7)
            end_date = end_date + datetime.timedelta(days=7)
        data = {}
        data['title'] = a.title
        data['digest'] = a.digest
        data['section'] = a.section.title
        data['start_date'] = start_date
        data['end_date'] = end_date
        initial.append(data)

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        formset = ActivityScheduleFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            schedule = Schedule()
            schedule.module = module
            schedule.title = form.cleaned_data.get("title").strip()
            schedule.default = form.cleaned_data.get("default")
            schedule.created_by = request.user
            
            # remvoe any existing default for this schedule
            if schedule.default:
                Schedule.objects.filter(module=module).update(default=False)
                
            schedule.save()
            
            for f in formset:
                act_sched = ActivitySchedule()
                start_date = f.cleaned_data.get("start_date")
                end_date = f.cleaned_data.get("end_date")
                digest = f.cleaned_data.get("digest")
                if start_date is not None:
                    act_sched = ActivitySchedule()
                    act_sched.schedule = schedule
                    act_sched.start_date = start_date
                    act_sched.end_date = end_date
                    act_sched.digest = digest.strip()
                    act_sched.save()
        return HttpResponseRedirect('../saved/')
    else:
        
        form = ScheduleForm()
        formset = ActivityScheduleFormSet(initial=initial)

    return render(request, 'learning_modules/schedule-form.html', {'form': form, 'formset': formset,'module':module, })

def schedule_saved(request, id):
    module = check_owner(request,id)
    return render_to_response('learning_modules/schedule-saved.html', 
                                    {'module': module},
                                  context_instance=RequestContext(request))
      
def check_owner(request,id):
    try:
        # check only the owner can view 
        if request.user.is_staff:
            module = Module.objects.get(pk=id)
        else:
            module = Module.objects.get(pk=id,user=request.user)
    except Module.DoesNotExist:
        raise Http404
    return module