# learning_modules/models.py
from django.db import models
from django.db.models import Max,Sum
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from xml.dom.minidom import *
import json
import datetime

class Module(models.Model):
    user = models.ForeignKey(User)
    created_date = models.DateTimeField('date created',default=datetime.datetime.now)
    lastupdated_date = models.DateTimeField('date updated',default=datetime.datetime.now)
    version = models.BigIntegerField()
    title = models.TextField(blank=False)
    shortname = models.CharField(max_length=20)
    filename = models.CharField(max_length=200)
    badge_icon = models.FileField(upload_to="badges",blank=True, default=None)
   
    class Meta:
        verbose_name = _('Module')
        verbose_name_plural = _('Modules')
        
    def __unicode__(self):
        return self.get_title(self)
    
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
     
    def is_first_download(self,user):
        no_attempts = ModuleDownload.objects.filter(user=user,module=self).count()
        is_first_download = False
        if no_attempts == 1:
            is_first_download = True
        return is_first_download
    
    def no_downloads(self):
        no_downloads = ModuleDownload.objects.filter(module=self).count()
        return no_downloads
    
    def no_distinct_downloads(self):
        no_distinct_downloads = ModuleDownload.objects.filter(module=self).values('user_id').distinct().count()
        return no_distinct_downloads
    
    def get_default_schedule(self):
        try:
            schedule = Schedule.objects.get(default=True,module = self)
        except Schedule.DoesNotExist:
            return None
        return schedule
    
class Tag(models.Model):
    name = models.TextField(blank=False)
    created_date = models.DateTimeField('date created',default=datetime.datetime.now)
    created_by = models.ForeignKey(User)
    modules = models.ManyToManyField(Module, through='ModuleTag')
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        
    def __unicode__(self):
        return self.name
 
class ModuleTag(models.Model):
    module = models.ForeignKey(Module)
    tag = models.ForeignKey(Tag)
    
    class Meta:
        verbose_name = _('Module Tag')
        verbose_name_plural = _('Module Tags')
           
class Schedule(models.Model):
    title = models.TextField(blank=False)
    module = models.ForeignKey(Module)
    default = models.BooleanField(default=False)
    created_date = models.DateTimeField('date created',default=datetime.datetime.now)
    lastupdated_date = models.DateTimeField('date updated',default=datetime.datetime.now)
    created_by = models.ForeignKey(User)
    
    class Meta:
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')
        
    def __unicode__(self):
        return self.title
    
    def to_xml_string(self):
        doc = Document();
        schedule = doc.createElement('schedule')
        schedule.setAttribute('version',self.lastupdated_date.strftime('%Y%m%d%H%M%S'))
        doc.appendChild(schedule)
        act_scheds = ActivitySchedule.objects.filter(schedule=self)
        for acts in act_scheds:
            act = doc.createElement('activity')
            act.setAttribute('digest',acts.digest)
            act.setAttribute('startdate',acts.start_date.strftime('%Y-%m-%d %H:%M:%S'))
            act.setAttribute('enddate',acts.end_date.strftime('%Y-%m-%d %H:%M:%S'))
            schedule.appendChild(act)
        return doc.toxml()
        
class ActivitySchedule(models.Model):
    schedule = models.ForeignKey(Schedule)
    digest = models.CharField(max_length=100)
    start_date = models.DateTimeField(default=datetime.datetime.now)
    end_date = models.DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        verbose_name = _('ActivitySchedule')
        verbose_name_plural = _('ActivitySchedules')
    
    
          
class Section(models.Model):
    module = models.ForeignKey(Module)
    order = models.IntegerField()
    title = models.TextField(blank=False)
    
    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')
        
    def __unicode__(self):
        return self.get_title()
    
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
        return self.get_title()
    
    class Meta:
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')
        
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
    
    class Meta:
        verbose_name = _('Media')
        verbose_name_plural = _('Media')
        
    def __unicode__(self):
        return self.filename
    
class Tracker(models.Model):
    user = models.ForeignKey(User)
    submitted_date = models.DateTimeField('date submitted',default=datetime.datetime.now)
    tracker_date = models.DateTimeField('date tracked',default=datetime.datetime.now)
    ip = models.IPAddressField()
    agent = models.TextField(blank=True)
    digest = models.CharField(max_length=100)
    data = models.TextField(blank=True)
    module = models.ForeignKey(Module,null=True, blank=True, default=None)
    type = models.CharField(max_length=10,null=True, blank=True, default=None)
    completed = models.BooleanField(default=False)
    time_taken = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _('Tracker')
        verbose_name_plural = _('Trackers')
        
    def __unicode__(self):
        return self.agent
    
    def is_first_tracker_today(self):
        olddate = datetime.datetime.now() + datetime.timedelta(hours=-24)
        no_attempts_today = Tracker.objects.filter(user=self.user,digest=self.digest,completed=True,submitted_date__gte=olddate).count()
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
            return a.get_title() + " (" + a.section.get_title() +")"
        media = Media.objects.filter(digest=self.digest)
        for m in media:
            return m.filename
        return "Not found"
    
    def activity_exists(self):
        activities = Activity.objects.filter(digest=self.digest).count()
        if activities >= 1:
            return True
        media = Media.objects.filter(digest=self.digest).count()
        if media >= 1:
            return True
        return False
 
    @staticmethod
    def has_completed_trackers(module,user):
        count = Tracker.objects.filter(user=user, module=module,completed=True).count()
        if count > 0:
            return True
        return False
     
    @staticmethod
    def to_xml_string(module,user):
        doc = Document();
        trackerXML = doc.createElement('trackers')
        doc.appendChild(trackerXML)
        trackers = Tracker.objects.filter(user=user, module=module,completed=True).values('digest').annotate(max_tracker=Max('submitted_date'))
        for t in trackers:
            track = doc.createElement('tracker')
            track.setAttribute('digest',t['digest'])
            track.setAttribute('submitteddate',t['max_tracker'].strftime('%Y-%m-%d %H:%M:%S'))
            trackerXML.appendChild(track)
        return doc.toxml() 
    
    @staticmethod
    def activity_views(user,type,start_date=None,end_date=None,module=None):
        results = Tracker.objects.filter(user=user,type=type)
        if start_date:
            results = results.filter(submitted_date__gte=start_date)
        if end_date:
            results = results.filter(submitted_date__lte=end_date)
        if module:
            results = results.filter(module=module)
        return results.count()
    
    @staticmethod
    def activity_secs(user,type,start_date=None,end_date=None,module=None):
        results = Tracker.objects.filter(user=user,type=type)
        if start_date:
            results = results.filter(submitted_date__gte=start_date)
        if end_date:
            results = results.filter(submitted_date__lte=end_date)
        if module:
            results = results.filter(module=module)
        time = results.aggregate(total=Sum('time_taken'))
        if time['total'] is None:
            return 0
        return time['total']
         
class ModuleDownload(models.Model):
    user = models.ForeignKey(User)
    module = models.ForeignKey(Module)
    download_date = models.DateTimeField('date downloaded',default=datetime.datetime.now)
    module_version = models.BigIntegerField(default=0)
    
    class Meta:
        verbose_name = _('ModuleDownload')
        verbose_name_plural = _('ModuleDownloads')
 
class Cohort(models.Model):
    module = models.ForeignKey(Module)  
    description = models.CharField(max_length=100)
    start_date = models.DateTimeField(default=datetime.datetime.now)
    end_date = models.DateTimeField(default=datetime.datetime.now)
    schedule = models.ForeignKey(Schedule,null=True, blank=True, default=None)
    
    class Meta:
        verbose_name = _('Cohort')
        verbose_name_plural = _('Cohorts')
        
    def __unicode__(self):
        return self.description
    
    @staticmethod
    def student_member_now(module,user):
        now = datetime.datetime.now()
        cohorts = Cohort.objects.filter(module=module,start_date__lte=now,end_date__gte=now)
        for c in cohorts:
            participants = c.participant_set.filter(user=user,role='student')
            for p in participants:
                return c
        return None
    
    @staticmethod
    def teacher_member_now(module,user):
        now = datetime.datetime.now()
        cohorts = Cohort.objects.filter(module=module,start_date__lte=now,end_date__gte=now)
        for c in cohorts:
            participants = c.participant_set.filter(user=user,role='teacher')
            for p in participants:
                return c
        return None
    
    @staticmethod
    def member_now(module,user):
        now = datetime.datetime.now()
        cohorts = Cohort.objects.filter(module=module,start_date__lte=now,end_date__gte=now)
        for c in cohorts:
            participants = c.participant_set.filter(user=user)
            for p in participants:
                return c
        return None
    
class Participant(models.Model):
    ROLE_TYPES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    cohort = models.ForeignKey(Cohort)
    user = models.ForeignKey(User)
    role = models.CharField(max_length=20,choices=ROLE_TYPES)
    
    class Meta:
        verbose_name = _('Participant')
        verbose_name_plural = _('Participants')
        
class Message(models.Model):
    module = models.ForeignKey(Module) 
    author = models.ForeignKey(User)
    date_created = models.DateTimeField(default=datetime.datetime.now)
    publish_date = models.DateTimeField(default=datetime.datetime.now)
    message = models.CharField(max_length=200)
    link = models.URLField(verify_exists=False,max_length=255)  
    icon = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')