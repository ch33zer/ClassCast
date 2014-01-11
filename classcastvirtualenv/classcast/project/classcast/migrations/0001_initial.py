# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'School'
        db.create_table(u'classcast_school', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal(u'classcast', ['School'])

        # Adding model 'Class'
        db.create_table(u'classcast_class', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classcast.School'])),
        ))
        db.send_create_signal(u'classcast', ['Class'])

        # Adding model 'CCUser'
        db.create_table(u'classcast_ccuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classcast.School'])),
            ('profpic', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'classcast', ['CCUser'])

        # Adding M2M table for field classes on 'CCUser'
        db.create_table(u'classcast_ccuser_classes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ccuser', models.ForeignKey(orm[u'classcast.ccuser'], null=False)),
            ('class', models.ForeignKey(orm[u'classcast.class'], null=False))
        ))
        db.create_unique(u'classcast_ccuser_classes', ['ccuser_id', 'class_id'])

        # Adding model 'Content'
        db.create_table(u'classcast_content', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('contentType', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('createDate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('editDate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('userDate', self.gf('django.db.models.fields.DateField')()),
            ('userowner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classcast.CCUser'])),
            ('classowner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classcast.Class'])),
        ))
        db.send_create_signal(u'classcast', ['Content'])

        # Adding model 'EmailSuffix'
        db.create_table(u'classcast_emailsuffix', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('suffix', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classcast.School'])),
        ))
        db.send_create_signal(u'classcast', ['EmailSuffix'])


    def backwards(self, orm):
        # Deleting model 'School'
        db.delete_table(u'classcast_school')

        # Deleting model 'Class'
        db.delete_table(u'classcast_class')

        # Deleting model 'CCUser'
        db.delete_table(u'classcast_ccuser')

        # Removing M2M table for field classes on 'CCUser'
        db.delete_table('classcast_ccuser_classes')

        # Deleting model 'Content'
        db.delete_table(u'classcast_content')

        # Deleting model 'EmailSuffix'
        db.delete_table(u'classcast_emailsuffix')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'classcast.ccuser': {
            'Meta': {'object_name': 'CCUser'},
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['classcast.Class']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'profpic': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['classcast.School']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'classcast.class': {
            'Meta': {'object_name': 'Class'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['classcast.School']"})
        },
        u'classcast.content': {
            'Meta': {'object_name': 'Content'},
            'classowner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['classcast.Class']"}),
            'contentType': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'createDate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'editDate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'userDate': ('django.db.models.fields.DateField', [], {}),
            'userowner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['classcast.CCUser']"})
        },
        u'classcast.emailsuffix': {
            'Meta': {'object_name': 'EmailSuffix'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['classcast.School']"}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'classcast.school': {
            'Meta': {'object_name': 'School'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['classcast']