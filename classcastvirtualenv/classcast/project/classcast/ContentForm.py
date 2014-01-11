from models import Content
from django.forms import ModelForm

class ContentForm(ModelForm):
	class Meta:
		model = Content
		fields = ['name','contentType','userDate']
