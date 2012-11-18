# mquiz_api/resources.py
from django.contrib.auth.models import User
from tastypie import fields, bundle
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication,Authentication
from tastypie.authorization import Authorization
from tastypie import http
from tastypie.exceptions import NotFound, BadRequest, InvalidFilterError, HydrationError, InvalidSortError, ImmediateHttpResponse
from learning_modules.models import Tracker
from learning_modules.api.serializers import PrettyJSONSerializer
from tastypie.validation import Validation
from django.http import HttpRequest

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        allowed_methods = ['get']
        authentication = BasicAuthentication()
        authorization = Authorization()  

class TrackerResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    class Meta:
        queryset = Tracker.objects.all()
        resource_name = 'tracker'
        allowed_methods = ['post']
        authentication = BasicAuthentication()
        authorization = Authorization() 
        serializer = PrettyJSONSerializer()
        always_return_data = True
        
    def hydrate(self, bundle, request=None):
        bundle.obj.user = User.objects.get(pk = bundle.request.user.id)
        bundle.obj.ip = bundle.request.get_host()
        bundle.obj.agent = bundle.request.META['HTTP_USER_AGENT']
        return bundle 