# mquiz_api/resources.py
from django.contrib.auth.models import User
from django.core import serializers
from tastypie import fields, bundle
from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie import http
from tastypie.exceptions import NotFound, BadRequest, InvalidFilterError, HydrationError, InvalidSortError, ImmediateHttpResponse
from learning_modules.models import Tracker, Module
from learning_modules.api.serializers import PrettyJSONSerializer, ModuleJSONSerializer
from tastypie.validation import Validation
from django.http import HttpRequest
from django.conf.urls.defaults import url
from tastypie.utils import trailing_slash
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
import os
import json

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        allowed_methods = ['get']

class TrackerResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    class Meta:
        queryset = Tracker.objects.all()
        resource_name = 'tracker'
        allowed_methods = ['post']
        authentication = ApiKeyAuthentication()
        authorization = Authorization() 
        serializer = PrettyJSONSerializer()
        always_return_data = True
        
    def hydrate(self, bundle, request=None):
        bundle.obj.user = User.objects.get(pk = bundle.request.user.id)
        bundle.obj.ip = bundle.request.get_host()
        bundle.obj.agent = bundle.request.META['HTTP_USER_AGENT']
        return bundle 
    
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
        return response
    
    def dehydrate(self, bundle):
        # Include full download url
        #bundle.data['url'] = settings.SITE_URL + bundle.data['resource_uri'] + 'download/'
        if bundle.request.is_secure():
            prefix = 'https://'
        else:
            prefix = 'http://'
        bundle.data['url'] = prefix + bundle.request.META['SERVER_NAME'] + bundle.data['resource_uri'] + 'download/'
        # make sure title is shown as json object (not string representation of one)
        bundle.data['title'] = json.loads(bundle.data['title'])
        return bundle