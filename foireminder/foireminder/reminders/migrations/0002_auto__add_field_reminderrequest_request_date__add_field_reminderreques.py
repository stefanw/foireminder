# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ReminderRequest.request_date'
        db.add_column('reminders_reminderrequest', 'request_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Adding field 'ReminderRequest.previous'
        db.add_column('reminders_reminderrequest', 'previous',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reminders.ReminderRequest'], null=True, on_delete=models.SET_NULL),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ReminderRequest.request_date'
        db.delete_column('reminders_reminderrequest', 'request_date')

        # Deleting field 'ReminderRequest.previous'
        db.delete_column('reminders_reminderrequest', 'previous_id')


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
        'reminders.foisite': {
            'Meta': {'object_name': 'FoiSite'},
            'country': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'example_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '10'}),
            'list_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'UTC'", 'max_length': '10'}),
            'tutorial': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'url_pattern': ('django.db.models.fields.CharField', [], {'default': "'.*'", 'max_length': '255'}),
            'url_pattern_make_request': ('django.db.models.fields.CharField', [], {'default': "'.*'", 'max_length': '255'})
        },
        'reminders.reminderrequest': {
            'Meta': {'object_name': 'ReminderRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'previous': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reminders.ReminderRequest']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'request_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'request_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'requested': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reminders.ReminderRule']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'reminders.reminderrule': {
            'Meta': {'object_name': 'ReminderRule'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'foisite': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reminders.FoiSite']"}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.IntegerField', [], {'default': '6', 'null': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        }
    }

    complete_apps = ['reminders']