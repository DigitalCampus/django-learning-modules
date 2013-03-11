# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Module'
        db.create_table('learning_modules_module', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('lastupdated_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('version', self.gf('django.db.models.fields.BigIntegerField')()),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('badge_icon', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('learning_modules', ['Module'])

        # Adding model 'Section'
        db.create_table('learning_modules_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['learning_modules.Module'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('title', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('learning_modules', ['Section'])

        # Adding model 'Activity'
        db.create_table('learning_modules_activity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['learning_modules.Section'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('digest', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('learning_modules', ['Activity'])

        # Adding model 'Media'
        db.create_table('learning_modules_media', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['learning_modules.Module'])),
            ('digest', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('download_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('learning_modules', ['Media'])

        # Adding model 'Tracker'
        db.create_table('learning_modules_tracker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('submitted_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('tracker_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('agent', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('digest', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['learning_modules.Module'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default=None, max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal('learning_modules', ['Tracker'])

        # Adding model 'ModuleDownload'
        db.create_table('learning_modules_moduledownload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['learning_modules.Module'])),
            ('download_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('module_version', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
        ))
        db.send_create_signal('learning_modules', ['ModuleDownload'])

        # Adding model 'Cohort'
        db.create_table('learning_modules_cohort', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['learning_modules.Module'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('learning_modules', ['Cohort'])

        # Adding model 'Participant'
        db.create_table('learning_modules_participant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cohort', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['learning_modules.Cohort'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('learning_modules', ['Participant'])

        # Adding model 'Message'
        db.create_table('learning_modules_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['learning_modules.Module'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=255)),
            ('icon', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('learning_modules', ['Message'])


    def backwards(self, orm):
        # Deleting model 'Module'
        db.delete_table('learning_modules_module')

        # Deleting model 'Section'
        db.delete_table('learning_modules_section')

        # Deleting model 'Activity'
        db.delete_table('learning_modules_activity')

        # Deleting model 'Media'
        db.delete_table('learning_modules_media')

        # Deleting model 'Tracker'
        db.delete_table('learning_modules_tracker')

        # Deleting model 'ModuleDownload'
        db.delete_table('learning_modules_moduledownload')

        # Deleting model 'Cohort'
        db.delete_table('learning_modules_cohort')

        # Deleting model 'Participant'
        db.delete_table('learning_modules_participant')

        # Deleting model 'Message'
        db.delete_table('learning_modules_message')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'learning_modules.activity': {
            'Meta': {'object_name': 'Activity'},
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['learning_modules.Section']"}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'learning_modules.cohort': {
            'Meta': {'object_name': 'Cohort'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['learning_modules.Module']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'learning_modules.media': {
            'Meta': {'object_name': 'Media'},
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'download_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['learning_modules.Module']"})
        },
        'learning_modules.message': {
            'Meta': {'object_name': 'Message'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['learning_modules.Module']"}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'learning_modules.module': {
            'Meta': {'object_name': 'Module'},
            'badge_icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastupdated_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'version': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'learning_modules.moduledownload': {
            'Meta': {'object_name': 'ModuleDownload'},
            'download_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['learning_modules.Module']"}),
            'module_version': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'learning_modules.participant': {
            'Meta': {'object_name': 'Participant'},
            'cohort': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['learning_modules.Cohort']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'learning_modules.section': {
            'Meta': {'object_name': 'Section'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['learning_modules.Module']"}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'learning_modules.tracker': {
            'Meta': {'object_name': 'Tracker'},
            'agent': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['learning_modules.Module']", 'null': 'True', 'blank': 'True'}),
            'submitted_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'tracker_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'type': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['learning_modules']