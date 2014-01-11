from django.db import models
from django.contrib.auth.models import User
from utils import unique_slugify
import random
import string

class School(models.Model):
    name = models.CharField(max_length=1000)
    slug = models.SlugField(blank=True,unique=True,max_length=200)

    def __unicode__(self):
        return self.name+":"+self.slug

    def save(self, **kwargs):
        if self.pk is None:
            slug = '%s' % (self.name)
            unique_slugify(self, slug)
        super(School, self).save(**kwargs)

class Class(models.Model):
    name = models.CharField(max_length=1000)
    school = models.ForeignKey(School)
    slug = models.SlugField(blank=True,unique=True,max_length=200)
    
    def __unicode__(self):
        return self.name+":"+self.slug

    def num_users(self):
        return self.ccuser_set.all().count()

    def save(self, **kwargs):
        if self.pk is None:
            slug = '%s %s' % (self.school.name,self.name)
            unique_slugify(self, slug)
        super(Class, self).save(**kwargs)

class CCUser(models.Model):
    user = models.OneToOneField(User,unique=True)
    school = models.ForeignKey(School)
    classes = models.ManyToManyField(Class)
    streamkey = models.CharField(max_length=41,db_index=True,unique=True)
    viewkey = models.CharField(max_length=41,db_index=True,unique=True)
    profpic = models.ImageField(upload_to=lambda instance,filename: "/".join(["profpics",instance.user.username,filename]))
    def __unicode__(self):
        return self.user.username

    def __gen_stream_key(self):
        r=random.SystemRandom()
        keylen = 40
        key = None
        while True:
            key = ''.join(r.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(keylen))
            if not CCUser.objects.filter(streamkey=key).exists():
                break
        self.streamkey = key

    def __gen_view_key(self):
        r=random.SystemRandom()
        keylen = 40
        key = None
        while True:
            key = ''.join(r.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(keylen))
            if not CCUser.objects.filter(viewkey=key).exists():
                break
        self.viewkey = key

    def get_user_stream(self):
        try:
            stream = self.stream
        except Stream.DoesNotExist:
            stream = None
        return stream

    def save(self,**kwargs):
        if self.pk is None:
            self.__gen_stream_key()
            self.__gen_view_key()
        super(CCUser,self).save(**kwargs)

class Content(models.Model):
    name = models.CharField(max_length=1000)
    contentType = models.CharField(max_length=200)
    createDate = models.DateField(auto_now_add=True)
    editDate = models.DateField(auto_now=True)
    userDate = models.DateField()
    userowner = models.ForeignKey(CCUser)
    classowner = models.ForeignKey(Class)
    schoolowner = models.ForeignKey(School)
    content = models.FileField(upload_to=lambda instance,filename: "/".join(["content",instance.schoolowner.name,instance.classowner.name,instance.userowner.user.username,filename]))
    slug = models.SlugField(blank=True,unique=True,max_length=200)

    def save(self, **kwargs):
        if self.pk is None:
            slug = '%s' % (self.name,)
            unique_slugify(self, slug)
        super(Content, self).save(**kwargs)

    def __unicode__(self):
        return self.name

class EmailSuffix(models.Model):
    suffix = models.CharField(max_length=200,unique=True,db_index=True)
    school = models.ForeignKey(School)
    def __unicode__(self):
        return self.suffix

class Stream(models.Model):
    userowner = models.OneToOneField(CCUser)
    classowner = models.ForeignKey(Class)
    viewers = models.PositiveIntegerField()

    def __unicode__(self):
        return self.userowner.user.username + "'s stream of class " + self.classowner.name

    def relative_name(self):
        return "classcast/"+self.userowner.user.username


class PermFakeModel(models.Model):
    pass