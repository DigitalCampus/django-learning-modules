# learning_modules/models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Module(models.Model):
    user = models.ForeignKey(User)
    created_date = models.DateTimeField('date created',default=datetime.now)
    lastupdated_date = models.DateTimeField('date updated',default=datetime.now)
    version = models.IntegerField()
    title = models.TextField(blank=False)
    shortname = models.CharField(max_length=20)
    filename = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.title
    
class Section(models.Model):
    module = models.ForeignKey(Module)
    order = models.IntegerField()
    title = models.TextField(blank=False)
    
    def __unicode__(self):
        return self.title
    
class Activity(models.Model):
    section = models.ForeignKey(Section)
    order = models.IntegerField()
    title = models.TextField(blank=False)
    type = models.CharField(max_length=10)
    digest = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.title