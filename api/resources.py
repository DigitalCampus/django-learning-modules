# learning_modules/api/resources.py
from django.contrib.auth.models import User
from django.core import serializers
from django.conf import settings
from tastypie import fields, bundle
from tastypie.resources import ModelResource, convert_post_to_patch, dict_strip_unicode_keys
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie import http
from tastypie.exceptions import NotFound, BadRequest, InvalidFilterError, HydrationError, InvalidSortError, ImmediateHttpResponse
from learning_modules.models import Activity, Section, Tracker, Module, ModuleDownload, Media, Schedule, ActivitySchedule, Cohort, Tag, ModuleTag
from learning_modules.api.serializers import PrettyJSONSerializer, ModuleJSONSerializer, TagJSONSerializer
from tastypie.validation import Validation
from django.http import HttpRequest
from django.conf.urls.defaults import url
from tastypie.utils import trailing_slash
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
import os
import json
import zipfile
import shutil
import datetime
from badges.models import Points, Award
from learning_modules.signals import module_downloaded

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        allowed_methods = ['get']

class TrackerResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    points = fields.IntegerField(readonly=True)
    badges = fields.IntegerField(readonly=True)
    
    class Meta:
        queryset = Tracker.objects.all()
        resource_name = 'tracker'
        allowed_methods = ['post','patch','put']
        detail_allowed_methods = ['post','patch','put']
        authentication = ApiKeyAuthentication()
        authorization = Authorization() 
        serializer = PrettyJSONSerializer()
        always_return_data =  True
        fields = ['points','digest','data','tracker_date','badges','module','completed']
        
    def is_valid(self, bundle, request=None):
        digest = bundle.data['digest']
        exists = False
        try:
            activity = Activity.objects.get(digest=bundle.data['digest'])
            exists = True
        except Activity.DoesNotExist:
            pass
        
        try:
            media = Media.objects.get(digest=bundle.data['digest'])
            exists = True
        except Media.DoesNotExist:
            pass
        
        if not exists:
            raise NotFound
            
    def hydrate(self, bundle, request=None):
        # remove any id if this is submitted - otherwise it may overwrite existing tracker item
        if 'id' in bundle.data:
            del bundle.data['id']
        bundle.obj.user = bundle.request.user
        bundle.obj.ip = bundle.request.META.get('REMOTE_ADDR','0.0.0.0')
        bundle.obj.agent = bundle.request.META.get('HTTP_USER_AGENT','unknown')
            
        # find out the module & activity type from the digest
        try:
            activity = Activity.objects.get(digest=bundle.data['digest'])
            bundle.obj.module = activity.section.module
            bundle.obj.type = activity.type
        except Activity.DoesNotExist:
            pass
        
        try:
            media = Media.objects.get(digest=bundle.data['digest'])
            bundle.obj.module = media.module
            bundle.obj.type = 'media'
        except Media.DoesNotExist:
            pass
        
        # this try/except block is temporary until everyone is using client app v17
        try:
            json_data = json.loads(bundle.data['data'])
            if json_data['activity'] == "completed":
                bundle.obj.completed = True
        except:
            pass
        
        try:
            json_data = json.loads(bundle.data['data'])
            if json_data['timetaken']:
                bundle.obj.time_taken = json_data['timetaken']
        except:
            pass
        
        return bundle 
    
    def dehydrate_points(self,bundle):
        points = Points.get_userscore(bundle.request.user)
        return points
    
    def dehydrate_badges(self,bundle):
        badges = Award.get_userawards(bundle.request.user)
        return badges
    
    def patch_list(self,request,**kwargs):
        request = convert_post_to_patch(request)
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        for data in deserialized["objects"]:
            data = self.alter_deserialized_detail_data(request, data)
            bundle = self.build_bundle(data=dict_strip_unicode_keys(data))
            bundle.request.user = request.user
            bundle.request.META['REMOTE_ADDR'] = request.META.get('REMOTE_ADDR','0.0.0.0')
            bundle.request.META['HTTP_USER_AGENT'] = request.META.get('HTTP_USER_AGENT','unknown')
            self.obj_create(bundle, request=request)
        response_data = {'points': self.dehydrate_points(bundle),'badges':self.dehydrate_badges(bundle)}
        response = HttpResponse(content=json.dumps(response_data),content_type="application/json; charset=utf-8")
        return response
    
class ModuleResource(ModelResource):
    
    class Meta:
        queryset = Module.objects.all()
        resource_name = 'module'
        allowed_methods = ['get']
        fields = ['id', 'title', 'version', 'shortname']
        authentication = ApiKeyAuthentication()
        authorization = Authorization() 
        serializer = ModuleJSONSerializer()
        always_return_data = True
        include_resource_uri = True
        
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/download%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('download_detail'), name="api_download_detail"),
            ]
    
    def download_detail(self, request, **kwargs):
        self.is_authenticated(request)
        self.throttle_check(request)
        
        pk = kwargs.pop('pk', None)
        module = self._meta.queryset.get(pk = pk)
        
        file_to_download = module.getAbsPath();
        schedule = module.get_default_schedule()
        has_completed_trackers = Tracker.has_completed_trackers(module,request.user)
        cohort = Cohort.member_now(module,request.user)
        if cohort:
            if cohort.schedule:
                schedule = cohort.schedule
        
        # add scheduling XML file     
        if schedule or has_completed_trackers:
            file_to_download = settings.MODULE_UPLOAD_DIR +"temp/"+ str(request.user.id) + "-" + module.filename
            shutil.copy2(module.getAbsPath(), file_to_download)
            zip = zipfile.ZipFile(file_to_download,'a')
            if schedule:
                zip.writestr(module.shortname +"/schedule.xml",schedule.to_xml_string())
            if has_completed_trackers:
                zip.writestr(module.shortname +"/tracker.xml",Tracker.to_xml_string(module,request.user))
            zip.close()

        wrapper = FileWrapper(file(file_to_download))
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Length'] = os.path.getsize(file_to_download)
        response['Content-Disposition'] = 'attachment; filename="%s"' %(module.filename)
        
        md = ModuleDownload()
        md.user = request.user
        md.module = module
        md.module_version = module.version
        md.save()
        
        module_downloaded.send(sender=self, module=module, user=request.user)
        
        return response
    
    def dehydrate(self, bundle):
        # Include full download url
        if bundle.request.is_secure():
            prefix = 'https://'
        else:
            prefix = 'http://'
        bundle.data['url'] = prefix + bundle.request.META['SERVER_NAME'] + bundle.data['resource_uri'] + 'download/'
        # make sure title is shown as json object (not string representation of one)
        bundle.data['title'] = json.loads(bundle.data['title'])
        
        module = Module.objects.get(pk=bundle.obj.pk)
        schedule = module.get_default_schedule()
        cohort = Cohort.member_now(module,bundle.request.user)
        if cohort:
            if cohort.schedule:
                schedule = cohort.schedule
        if schedule:
            bundle.data['schedule'] = schedule.lastupdated_date.strftime("%Y%m%d%H%M%S")
            sr = ScheduleResource()
            bundle.data['schedule_uri'] = sr.get_resource_uri(schedule)
        
        return bundle
  
class ModuleTagResource(ModelResource):
    module = fields.ToOneField('learning_modules.api.resources.ModuleResource', 'module', full=True)
    class Meta:
        queryset = ModuleTag.objects.all()
        allowed_methods = ['get','post']
        fields = ['id','module','tag']
        include_resource_uri = False
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        always_return_data = True
      
      
class ScheduleResource(ModelResource):
    activityschedule = fields.ToManyField('learning_modules.api.resources.ActivityScheduleResource', 'activityschedule_set', related_name='schedule', full=True, null=True)
    class Meta:
        queryset = Schedule.objects.all()
        resource_name = 'schedule'
        allowed_methods = ['get']
        fields = ['id', 'title', 'lastupdated_date']
        authentication = ApiKeyAuthentication()
        authorization = Authorization() 
        always_return_data = True
        include_resource_uri = False
       
    def dehydrate(self, bundle):
        bundle.data['version'] = bundle.data['lastupdated_date'].strftime("%Y%m%d%H%M%S")
        return bundle 
   
class TagResource(ModelResource):
    count = fields.IntegerField(readonly=True)
    modules = fields.ToManyField('learning_modules.api.resources.ModuleTagResource', 'moduletag_set', related_name='tag', full=True)

    class Meta:
        queryset = Tag.objects.filter(modules__isnull=False).distinct().order_by("name")
        resource_name = 'tag'
        allowed_methods = ['get']
        fields = ['id','name']
        authentication = ApiKeyAuthentication()
        authorization = Authorization() 
        always_return_data = True
        include_resource_uri = False
        serializer = TagJSONSerializer()
    
    def dehydrate(self,bundle):
        return bundle
    
    def dehydrate_count(self,bundle):
        count = Module.objects.filter(tag__id=bundle.obj.id).count()
        return count
    
    def tag_detail(self, request, **kwargs):
        self.is_authenticated(request)
        self.throttle_check(request)
        
        name = kwargs.pop('name', None)
        modules = Module.objects.filter(tag__name=name)
        
        for m in modules:
            obj = ModuleResource().build_bundle(obj=m, request=request)
            
        response = HttpResponse(name+str(modules), content_type='')
        return response
             
class ActivityScheduleResource(ModelResource):
    schedule = fields.ToOneField('learning_modules.api.resources.ScheduleResource', 'schedule', related_name='activityschedule')
    class Meta:
        queryset = ActivitySchedule.objects.all()
        resource_name = 'activityschedule'
        allowed_methods = ['get']
        fields = ['digest', 'start_date', 'end_date']
        authentication = ApiKeyAuthentication()
        authorization = Authorization() 
        always_return_data = True
        include_resource_uri = False
        
    def dehydrate(self, bundle):
        bundle.data['start_date'] = bundle.data['start_date'].strftime("%Y-%m-%d %H:%M:%S")
        bundle.data['end_date'] = bundle.data['end_date'].strftime("%Y-%m-%d %H:%M:%S")
        return bundle
    
class ScorecardResource(ModelResource):
    media_views = fields.IntegerField(readonly=True)
    media_points = fields.IntegerField(readonly=True)
    media_secs = fields.IntegerField(readonly=True)
   
    page_views = fields.IntegerField(readonly=True)
    page_points = fields.IntegerField(readonly=True)
    page_secs = fields.IntegerField(readonly=True)
    
    quiz_views = fields.IntegerField(readonly=True)
    quiz_points = fields.IntegerField(readonly=True)
    quiz_secs = fields.IntegerField(readonly=True)
    
    class Meta:
        queryset = User.objects.all()
        resource_name = 'scorecard'
        allowed_methods = ['get']
        fields = ['first_name', 'last_name']
        authentication = ApiKeyAuthentication()
        authorization = Authorization() 
        serializer= PrettyJSONSerializer()
        always_return_data = True
        include_resource_uri = False
        
    def dehydrate_media_views(self,bundle):
        start_date = datetime.datetime.now() - datetime.timedelta(days=14)
        end_date = datetime.datetime.now()
        return Tracker.activity_views(user=bundle.obj,type='media',start_date=start_date,end_date=end_date)
    
    def dehydrate_media_points(self,bundle):
        start_date = datetime.datetime.now() - datetime.timedelta(days=14)
        end_date = datetime.datetime.now()
        return Points.media_points(user=bundle.obj,start_date=start_date,end_date=end_date)
    
    def dehydrate_media_secs(self,bundle):
        start_date = datetime.datetime.now() - datetime.timedelta(days=14)
        end_date = datetime.datetime.now()
        return Tracker.activity_secs(user=bundle.obj,type='media',start_date=start_date,end_date=end_date)
    
    def dehydrate_page_views(self,bundle):
        start_date = datetime.datetime.now() - datetime.timedelta(days=14)
        end_date = datetime.datetime.now()
        return Tracker.activity_views(user=bundle.obj,type='page',start_date=start_date,end_date=end_date)
    
    def dehydrate_page_points(self,bundle):
        start_date = datetime.datetime.now() - datetime.timedelta(days=14)
        end_date = datetime.datetime.now()
        return Points.page_points(user=bundle.obj,start_date=start_date,end_date=end_date)
    
    def dehydrate_page_secs(self,bundle):
        start_date = datetime.datetime.now() - datetime.timedelta(days=14)
        end_date = datetime.datetime.now()
        return Tracker.activity_secs(user=bundle.obj,type='page',start_date=start_date,end_date=end_date)
    
    def dehydrate_quiz_views(self,bundle):
        start_date = datetime.datetime.now() - datetime.timedelta(days=14)
        end_date = datetime.datetime.now()
        return Tracker.activity_views(user=bundle.obj,type='quiz',start_date=start_date,end_date=end_date)
    
    def dehydrate_quiz_points(self,bundle):
        start_date = datetime.datetime.now() - datetime.timedelta(days=14)
        end_date = datetime.datetime.now()
        return Points.quiz_points(user=bundle.obj,start_date=start_date,end_date=end_date)
    
    def dehydrate_quiz_secs(self,bundle):
        start_date = datetime.datetime.now() - datetime.timedelta(days=14)
        end_date = datetime.datetime.now()
        return Tracker.activity_secs(user=bundle.obj,type='quiz',start_date=start_date,end_date=end_date)