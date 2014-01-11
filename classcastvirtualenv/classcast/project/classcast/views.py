from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden

from models import *

from django.db.models import F

from forms import ContentForm, UserCreateForm, ClassForm

from django.shortcuts import get_object_or_404, render

from django.contrib.auth import authenticate, login

from django.contrib.auth.models import User, Permission

from django.core.urlresolvers import reverse

from django.views.generic.edit import FormView

from django.contrib import messages

from django.contrib.formtools.wizard.views import SessionWizardView

from django.contrib.auth.decorators import login_required

from django.contrib.contenttypes.models import ContentType

from django.views.decorators.csrf import csrf_exempt

from django.core.exceptions import ObjectDoesNotExist

from django.utils.http import urlencode

import json

import tldextract

def getschoolpermname(slug):
    name = "in_school_"+slug
    if len(name)>40:
        name = name[:20] + str(hash(name[20:]))
    return name
def createschoolperm(slug):
    ct = ContentType.objects.get_for_model(PermFakeModel)
    Permission.objects.create(codename=getschoolpermname(slug),
        name="School perm",
        content_type=ct)
def getschoolperm(slug):
    return Permission.objects.get(codename=getschoolpermname(slug))

def requireschoolperm(request,slug):
    if not request.user.is_authenticated():
        messages.error(request,"Forbidden. Log in to view this page.")
        return HttpResponseRedirect("/")
    if not request.user.has_perm("classcast."+getschoolpermname(slug)):
        messages.error(request,"You don't have access to this page.")
        return HttpResponseRedirect("/")
    return

def getclasspermname(slug):
    name = "in_class_"+slug
    if len(name)>40:
        name = name[:20] + str(hash(name[20:]))
    return name
def createclassperm(slug):
    ct = ContentType.objects.get_for_model(PermFakeModel)
    perm = Permission.objects.create(codename=getclasspermname(slug),
        name="Class perm",
        content_type=ct)
def getclassperm(slug):
    return Permission.objects.get(codename=getclasspermname(slug))

def requireclassperm(request,slug):
    if not request.user.is_authenticated():
        messages.error(request,"Forbidden. Log in to view this page.")
        return HttpResponseRedirect("/")
    if not request.user.has_perm("classcast."+getclasspermname(slug)):
        messages.error(request,"You don't have access to this page.")
        return HttpResponseRedirect("/")
    return

def indexview(request):
    return render(request,'classcast/index.html',{})

def schoolview(request, schoolslug):
    school = get_object_or_404(School, slug=schoolslug)
    return render(request,'classcast/school.html',{"school":school})

def classview(request,classslug):
    resp = requireclassperm(request,classslug)
    if resp:
        return resp
    classobj = get_object_or_404(Class, slug=classslug)
    school = classobj.school
    return render(request, 'classcast/class.html',{"school":school,"class":classobj})

def streamview(request,classslug):
    resp = requireclassperm(request,classslug)
    if resp:
        return resp
    classobj = get_object_or_404(Class, slug=classslug)
    server = "rtmp://54.193.77.36/classcast/"
    stream = request.user.username
    streamkey = request.user.ccuser.streamkey
    return render(request,'classcast/stream.html',{"class":classobj,"server":server,"stream":stream,"streamkey":streamkey})

def userview(request,userid):
    ccuser = get_object_or_404(CCUser,pk=userid)
    return render(request, 'classcast/user.html',{"pageccuser":ccuser,"pageuser":ccuser.user})

#TODO, implement this
def is_local(request):
    return request.META.REMOTE_ADDR == "127.0.0.1"

@csrf_exempt
def on_publish(request):
    print "on_publish"
    if request.method == 'POST':
        post = request.POST
        if "streamkey" in post and "classslug" in post and "name" in post:
            streamkey = post["streamkey"]
            classslug = post["classslug"]
            name = post["name"]
            try:
                user = CCUser.objects.get(user__username=name,streamkey=streamkey)
            except ObjectDoesNotExist:
                return HttpResponseForbidden("Streamkey not recognized for user")
            try:
                classobj = Class.objects.get(slug=classslug)
            except ObjectDoesNotExist:
                return HttpResponseForbidden("Classslug not recognized")
            if user.get_user_stream():
                return HttpResponseBadRequest('User is already streaming')
            if classobj not in user.classes.all():
                return HttpResponseForbidden("You must be in the class to stream it")
            new_stream = Stream()
            new_stream.userowner = user
            new_stream.classowner = classobj
            new_stream.viewers=0
            new_stream.save()
            print "on_publish succeeded"
            return HttpResponse(json.dumps({"status":"ok"}))
        else:
            print post
            return HttpResponseBadRequest('"streamkey", "classslug" and "name" required')
    else:
        return HttpResponseNotAllowed(['POST'],'Only post allowed')

@csrf_exempt
def on_publish_done(request):
    print "on_publish_done"
    if request.method == 'POST':
        post = request.POST
        if "name" in post:
            name = post["name"]
            try:
                user = CCUser.objects.get(user__username=name)
            except ObjectDoesNotExist:
                return HttpResponseForbidden("User not recognized")
            user.stream.delete()
            print "on_publish_done succeeded"
            return HttpResponse(json.dumps({"status":"ok"}))
        else:
            return HttpResponseBadRequest('"name" required')
    else:
        return HttpResponseNotAllowed(['POST'],'Only post allowed')

@csrf_exempt
def on_play(request):
    print "on_play"
    if request.method == 'POST':
        post = request.POST
        if "viewkey" in post and "name" in post:
            viewkey = post["viewkey"]
            name = post["name"]
            try:
                user = CCUser.objects.get(viewkey=viewkey)
            except ObjectDoesNotExist:
                return HttpResponseForbidden("Viewkey not recognized for user")
            try:
                stream = Stream.objects.get(userowner__user__username=name)
            except ObjectDoesNotExist:
                return HttpResponseForbidden("Stream not recognized")
            if stream.classowner not in user.classes.all():
                return HttpResponseForbidden("You must be in the class to watch the stream")
            stream.viewers = F('viewers') + 1
            stream.save()
            print "on_play succeeded"
            return HttpResponse(json.dumps({"status":"ok"}))
        else:
            return HttpResponseBadRequest('"viewkey" and "name" required')
    else:
        return HttpResponseNotAllowed(['POST'],'Only post allowed')

@csrf_exempt
def on_play_done(request):
    if request.method == 'POST':
        post = request.POST
        if "name" in post:
            name = post["name"]
            try:
                stream = Stream.objects.get(userowner__user__username=name)
            except ObjectDoesNotExist:
                return HttpResponseForbidden("Stream not recognized")
            stream.viewers = F('viewers') - 1
            stream.save()
            return HttpResponse(json.dumps({"status":"ok"}))
        else:
            return HttpResponseBadRequest('"viewkey" and "name" required')
    else:
        return HttpResponseNotAllowed(['POST'],'Only post allowed')



def contentview(request,contentslug):
    content = get_object_or_404(Content,slug=contentslug)
    resp = requireclassperm(request,content.classowner.slug)
    if resp:
        return resp
    return render(request, 'classcast/content.html',{"classcontent":content})

@login_required
def addclass(request):
    if request.method == 'POST':
        if 'slug' in request.POST and 'op' in request.POST:
            slug = request.POST['slug']
            add = request.POST['op'] == 'sub';
            classobj=get_object_or_404(Class,slug=slug)
            user=request.user.ccuser
            if add:
                resp = requireschoolperm(request,classobj.school.slug)
                if resp:
                    return resp
                user.classes.add(classobj)
                request.user.user_permissions.add(getclassperm(slug))
            else:
                user.classes.remove(classobj)
                request.user.user_permissions.remove(getclassperm(slug))
            return HttpResponse(json.dumps({"status":"ok"}))
        else:
            return HttpResponseBadRequest('"slug" and "op" required')
    else:
        return HttpResponseNotAllowed(['POST'],'Only post allowed')

@login_required
def addcontentview(request,classslug):
    resp = requireclassperm(request,classslug)
    if resp:
        return resp
    classobj = get_object_or_404(Class, slug=classslug)
    school = classobj.school
    if request.method == 'POST': # If the form has been submitted...
        form = ContentForm(request.POST,request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            newcontent = form.save(commit=False)
            newcontent.classowner = classobj
            newcontent.schoolowner = school
            newcontent.userowner = request.user.ccuser
            newcontent.save()
            form.save_m2m()

            messages.success(request, "Content added")

            return HttpResponseRedirect(reverse('classcast:classview', args=(classobj.slug,))) # Redirect after POST
        else:
            messages.error(request, "Upload failed. See below.")
    else:
        form = ContentForm() # An unbound form

    return render(request, 'classcast/addcontent.html',{"school":school,"class":classobj,"form":form})

def get_suffix(email):
    return '.'.join(tldextract.extract(email)[-2:])

def email_of_new_school(email):
    suffix = get_suffix(email)
    return not EmailSuffix.objects.filter(suffix=suffix).exists()

def is_new_school(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('userform') or {'email': 'none'}
    return email_of_new_school(cleaned_data["email"])

class CreateClassView(FormView):
    template_name = "classcast/createclass.html"
    form_class = ClassForm
    def form_valid(self,form):
        request = self.request
        if not request.user.is_authenticated():
            messages.error(request,"You must log in")
            return HttpResponseRedirect("/")
        newclass = form.save(commit=False)
        newclass.school = request.user.ccuser.school
        newclass.save()
        form.save_m2m()
        request.user.ccuser.classes.add(newclass)
        createclassperm(newclass.slug)
        request.user.user_permissions.add(getclassperm(newclass.slug))
        return HttpResponseRedirect(reverse('classcast:classview',args=(newclass.slug,)))

class RegistrationWizard(SessionWizardView):
    templates = {
        "userform":"registration/register.html",
        "schoolform":"registration/schoolentry.html"
    }
    def done(self,form_list,**kwargs):
        userform = form_list[0] #always will be at least 1 form
        usercleaned = userform.cleaned_data
        email = usercleaned["email"]
        name = usercleaned["username"]
        email_suffix = get_suffix(email)
        password = usercleaned["password1"]
        new_user = User.objects.create_user(name,email,password) #Username, email, password
        new_user.save()
        new_ccuser = CCUser()
        new_ccuser.user=new_user
        school = None
        if email_of_new_school(email):
            schoolform = form_list[1]
            schoolcleaned = schoolform.cleaned_data
            schoolname = schoolcleaned["name"]
            new_school = None
            if not School.objects.filter(name=schoolname).exists():
                new_school = School()
                new_school.name = schoolname
                new_school.save()
                createschoolperm(new_school.slug)
            else:
                new_school = School.objects.get(name=schoolname)
            new_suffix = EmailSuffix()
            new_suffix.school = new_school
            new_suffix.suffix = email_suffix
            new_suffix.save()
            school = new_school
        else:
            suffix=EmailSuffix.objects.get(suffix=email_suffix)
            school=suffix.school
        new_ccuser.school = school
        new_ccuser.save()
        user = authenticate(username=new_user.username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                user.user_permissions.add(getschoolperm(school.slug))
                return HttpResponseRedirect(reverse('classcast:schoolview',args=(school.slug,)))
        messages.error(self.request,"Something went wrong with registration")
        return HttpResponseRedirect("/")

    def get_context_data(self, form, **kwargs):
        context = super(RegistrationWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'schoolform':
            context.update({'schools': json.dumps([ school.name for school in School.objects.all()])})
        return context

    def get_template_names(self):
        return [RegistrationWizard.templates[self.steps.current]]