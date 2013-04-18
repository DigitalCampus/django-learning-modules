# learning_modules/admin.py
from learning_modules.models import Module,Section, Activity, Tracker, Media, Cohort, Participant, Message
from django.contrib import admin


class TrackerAdmin(admin.ModelAdmin):
    list_display = ('user', 'submitted_date', 'agent', 'module')

admin.site.register(Module)
admin.site.register(Section)
admin.site.register(Activity)
admin.site.register(Tracker, TrackerAdmin)
admin.site.register(Media)
admin.site.register(Cohort)
admin.site.register(Participant)
admin.site.register(Message)
