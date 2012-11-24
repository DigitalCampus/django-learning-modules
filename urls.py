# learning_modules/urls.py
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from learning_modules.api.resources import TrackerResource

from tastypie.api import Api
v1_api = Api(api_name='v1')
v1_api.register(TrackerResource())

urlpatterns = patterns('',

    url(r'^$', 'learning_modules.views.home_view', name="modules_home"),
    url(r'^upload/$', 'learning_modules.views.upload', name="modules_upload"),
    url(r'^upload/success/$', direct_to_template, {"template": "learning_modules/upload-success.html",}, name="modules_upload_success"),
    (r'^api/', include(v1_api.urls)),

)
