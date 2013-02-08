# learning_modules/urls.py
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from learning_modules.api.resources import TrackerResource, ModuleResource

from tastypie.api import Api
v1_api = Api(api_name='v1')
v1_api.register(TrackerResource())
v1_api.register(ModuleResource())

urlpatterns = patterns('',

    url(r'^$', 'learning_modules.views.home_view', name="modules_home"),
    url(r'^upload/$', 'learning_modules.views.upload', name="modules_upload"),
    url(r'^upload/success/$', direct_to_template, {"template": "learning_modules/upload-success.html",}, name="modules_upload_success"),
    url(r'^(?P<id>\d+)/$', 'learning_modules.views.recent_activity', name="module_recent_activity"),
    (r'^api/', include(v1_api.urls)),

)
