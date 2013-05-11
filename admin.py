# learning_modules/admin.py
from learning_modules.models import *
from django.contrib import admin


class TrackerAdmin(admin.ModelAdmin):
    list_display = ('user', 'submitted_date', 'agent', 'module')
    
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'lastupdated_date', 'user', 'filename')

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('cohort', 'user', 'role')
   
class CohortAdmin(admin.ModelAdmin):
    list_display = ('module', 'description', 'start_date', 'end_date')
     
admin.site.register(Module,ModuleAdmin)
admin.site.register(Section)
admin.site.register(Activity)
admin.site.register(Tracker, TrackerAdmin)
admin.site.register(Media)
admin.site.register(Cohort, CohortAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Message)
admin.site.register(Schedule)
admin.site.register(ActivitySchedule)
admin.site.register(Tag)
