# learning_modules/models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
from badges.tasks import tracker_callback
import json

class Module(models.Model):
    user = models.ForeignKey(User)
    created_date = models.DateTimeField('date created',default=datetime.now)
    lastupdated_date = models.DateTimeField('date updated',default=datetime.now)
    version = models.BigIntegerField()
    title = models.TextField(blank=False)
    shortname = models.CharField(max_length=20)
    filename = models.CharField(max_length=200)
   
    def __unicode__(self):
        return self.title
    
    def getAbsPath(self):
        return settings.MODULE_UPLOAD_DIR + self.filename
    
    def get_title(self,lang='en'):
        try:
            titles = json.loads(self.title)
            if lang in titles:
                return titles[lang]
            else:
                for l in titles:
                    return titles[l]
        except:
            pass
        return self.title 
     
class Section(models.Model):
    module = models.ForeignKey(Module)
    order = models.IntegerField()
    title = models.TextField(blank=False)
    
    def __unicode__(self):
        return self.title
    
    def get_title(self,lang='en'):
        try:
            titles = json.loads(self.title)
            if lang in titles:
                return titles[lang]
            else:
                for l in titles:
                    return titles[l]
        except:
            pass
        return self.title
    
class Activity(models.Model):
    section = models.ForeignKey(Section)
    order = models.IntegerField()
    title = models.TextField(blank=False)
    type = models.CharField(max_length=10)
    digest = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.title

    def get_title(self,lang='en'):
        try:
            titles = json.loads(self.title)
            if lang in titles:
                return titles[lang]
            else:
                for l in titles:
                    return titles[l]
        except:
            pass
        return self.title
    
class Media(models.Model):
    module = models.ForeignKey(Module)
    digest = models.CharField(max_length=100)
    filename = models.CharField(max_length=200)
    download_url = models.URLField()
    
    def __unicode__(self):
        return self.filename
    
class Tracker(models.Model):
    user = models.ForeignKey(User)
    submitted_date = models.DateTimeField('date submitted',default=datetime.now)
    tracker_date = models.DateTimeField('date tracked',default=datetime.now)
    ip = models.IPAddressField()
    agent = models.TextField(blank=True)
    digest = models.CharField(max_length=100)
    data = models.TextField(blank=True)
    
    def is_first_tracker_today(self,user):
        date = datetime.now()
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%y")
        no_attempts_today = Tracker.objects.filter(user=user,digest=self.digest,submitted_date__day=day,submitted_date__month=month,submitted_date__year=year).count()
        if no_attempts_today == 1:
            return True
        else:
            return False
    
    def get_activity_type(self):
        activities = Activity.objects.filter(digest=self.digest)
        for a in activities:
            return a.type
        media = Media.objects.filter(digest=self.digest)
        for m in media:
            return "media"
        return None
        
    def get_activity_title(self):
        activities = Activity.objects.filter(digest=self.digest)
        for a in activities:
            return a.get_title() + " (" + a.section.module.get_title() + " / " + a.section.get_title() +")"
        media = Media.objects.filter(digest=self.digest)
        for m in media:
            return m.filename + " (" + m.module.get_title()+")"
        return "Not found"
    
models.signals.post_save.connect(tracker_callback, sender=Tracker)