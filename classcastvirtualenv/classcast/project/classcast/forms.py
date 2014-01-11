from models import Content, CCUser, EmailSuffix,School,Class
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
import registrationforms
import tldextract


class ContentForm(ModelForm):
    class Meta:
        model = Content
        fields = ['name','contentType','userDate','content']

class ClassForm(ModelForm):
    class Meta:
        model = Class
        fields = ['name']

class LoginForm(forms.Form):
    username=forms.CharField(label=".edu Email",required=True)
    password=forms.CharField(label="Password",widget=forms.PasswordInput,required=True)

class UserCreateForm(registrationforms.RegistrationFormUniqueEmail):
    def clean_email(self):
        email = super(UserCreateForm,self).clean_email()
        extracted = tldextract.extract(email)
        if extracted[-1] != 'edu':
            raise forms.ValidationError("You must have a .edu address to register")
        return email

class SchoolCreateForm(ModelForm):
    class Meta:
        model = School
        fields = ['name']
