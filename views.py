# learning_modules/views.py
from django.shortcuts import render,render_to_response
from django.template import RequestContext
from django.contrib.auth import (authenticate, logout, views)
from django.contrib.auth.models import User

from mquiz.models import Quiz

def home_view(request):
    latest_quiz_list = Quiz.objects.filter(draft=0).order_by('-created_date')[:10]
    return render_to_response('learning_modules/home.html',{'latest_quiz_list': latest_quiz_list}, context_instance=RequestContext(request))
