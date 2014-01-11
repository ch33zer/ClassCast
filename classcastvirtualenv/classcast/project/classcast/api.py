from tastypie.resources import ModelResource
from models import EmailSuffix, School

class EmailSuffixResource(ModelResource):
    class Meta:
        queryset = EmailSuffix.objects.all()
        resource_name = 'email_suffix'
        filtering = {
        	"suffix":("exact",)
        }

class SchoolResource(ModelResource):
    class Meta:
        queryset = School.objects.all()
        resource_name = 'school'

