# learning_modules/admin.py
from learning_modules.models import Module,Section, Activity, Tracker, Media, Cohort, Participant, Message
from django.contrib import admin

admin.site.register(Module)
admin.site.register(Section)
admin.site.register(Activity)
admin.site.register(Tracker)
admin.site.register(Media)
admin.site.register(Cohort)
admin.site.register(Participant)
admin.site.register(Message)
