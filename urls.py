# learning_modules/urls.py
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from tastypie.api import Api
v1_api = Api(api_name='v1')

urlpatterns = patterns('',

    url(r'^$', 'mquiz.views.home_view', name="mquiz_home"),
    (r'^api/', include(v1_api.urls)),

    

)
