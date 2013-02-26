# mquiz_api/resources.py
from django.contrib.auth.models import User
from django.core import serializers
from tastypie import fields, bundle
from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie import http
from tastypie.exceptions import NotFound, BadRequest, InvalidFilterError, HydrationError, InvalidSortError, ImmediateHttpResponse
from learning_modules.models import Tracker, Module, ModuleDownload
from learning_modules.api.serializers import PrettyJSONSerializer, ModuleJSONSerializer
from tastypie.validation import Validation
from django.http import HttpRequest
from django.conf.urls.defaults import url
from tastypie.utils import trailing_slash
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
import os
import json
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
        allowed_methods = ['post']
        authentication = ApiKeyAuthentication()
        authorization = Authorization() 
        serializer = PrettyJSONSerializer()
        always_return_data =  True
        fields = ['points','digest','data','tracker_date','badges']
        
    def hydrate(self, bundle, request=None):
        # remove any id if this is submitted - otherwise it may overwrite existing tracker item
        if 'id' in bundle.data:
            del bundle.data['id']
        bundle.obj.user = User.objects.get(pk = bundle.request.user.id)
        bundle.obj.ip = bundle.request.META.get('REMOTE_ADDR','0.0.0.0')
        bundle.obj.agent = bundle.request.META.get('HTTP_USER_AGENT','unknown')
        return bundle 
    
    def dehydrate_points(self,bundle):
        points = Points.get_userscore(bundle.request.user)
        return points
    
    def dehydrate_badges(self,bundle):
        badges = Award.get_userawards(bundle.request.user)
        return badges
    
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
        wrapper = FileWrapper(file(module.getAbsPath()))
        response = HttpResponse(wrapper, content_type='application/zip') #or whatever type you want there
        response['Content-Length'] = os.path.getsize(module.getAbsPath())
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
        return bundle
    