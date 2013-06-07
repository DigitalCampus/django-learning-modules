# learning_modules/urls.py
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from learning_modules.api.resources import TrackerResource, ModuleResource, ScheduleResource, TagResource, ScorecardResource

from tastypie.api import Api
v1_api = Api(api_name='v1')
v1_api.register(TrackerResource())
v1_api.register(ModuleResource())
v1_api.register(ScheduleResource())
v1_api.register(TagResource())
v1_api.register(ScorecardResource())

urlpatterns = patterns('',

    url(r'^$', 'learning_modules.views.home_view', name="modules_home"),
    url(r'^upload/$', 'learning_modules.views.upload', name="modules_upload"),
    url(r'^upload/success/$', direct_to_template, {"template": "learning_modules/upload-success.html",}, name="modules_upload_success"),
    url(r'^(?P<id>\d+)/$', 'learning_modules.views.recent_activity', name="module_recent_activity"),
    url(r'^(?P<id>\d+)/detail/$', 'learning_modules.views.recent_activity_detail', name="module_recent_activity_detail"),
    url(r'^(?P<module_id>\d+)/schedule/$', 'learning_modules.views.schedule', name="module_schedules"),
    url(r'^(?P<module_id>\d+)/schedule/add/$', 'learning_modules.views.schedule_add', name="module_schedule_add"),
    url(r'^(?P<module_id>\d+)/schedule/(?P<schedule_id>\d+)/edit/$', 'learning_modules.views.schedule_edit', name="module_schedule_edit"),
    url(r'^(?P<module_id>\d+)/schedule/saved/$', 'learning_modules.views.schedule_saved'),
    url(r'^(?P<module_id>\d+)/schedule/(?P<schedule_id>\d+)/saved/$', 'learning_modules.views.schedule_saved'),
    (r'^api/', include(v1_api.urls)),

)
