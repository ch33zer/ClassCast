from django.conf.urls import patterns, include, url

from django.contrib.auth.views import login, logout

from api import EmailSuffixResource, SchoolResource

from forms import UserCreateForm, SchoolCreateForm

from tastypie.api import Api

import views

def betterurl(regex, view):
	name = view.__name__
	return url(regex,view,name=name)


v1_api = Api(api_name='v1')
v1_api.register(SchoolResource())
v1_api.register(EmailSuffixResource())

schoolpatterns = patterns('',
	betterurl(r'^$',views.schoolview)
)

classpatterns = patterns('',
	betterurl(r'^$',views.classview),
	betterurl(r'^upload/?$',views.addcontentview),
    betterurl(r'^stream/?$',views.streamview)
)

contentpatterns = patterns('',
        betterurl(r'^$',views.contentview)
)

userpatterns = patterns('',
	betterurl(r'^$',views.userview)
)

forms = [
    ("userform",UserCreateForm),
    ("schoolform",SchoolCreateForm)
]
conditions = {
    "schoolform":views.is_new_school
}
urlpatterns = patterns('',
    betterurl(r'^$', views.indexview),
    url(r'^accounts/register/?$',views.RegistrationWizard.as_view(forms,condition_dict=conditions),name='registerview'),
    url(r'^accounts/login/?$', login, name='loginview'),
    url(r'^accounts/logout/?$', logout, {"next_page":"/"}, name='logoutview'),
    url(r'^school/(?P<schoolslug>[\w-]+)/',include(schoolpatterns)),
    url(r'^class/create/?$',views.CreateClassView.as_view(),name='createclassview'),
    url(r'^class/(?P<classslug>[\w-]+)/',include(classpatterns)),
    url(r'^user/(?P<userid>\d+)/',include(userpatterns)),
    url(r'^content/(?P<contentslug>[\w-]+)/',include(contentpatterns)),
    url(r'^api/',include(v1_api.urls)),
    url(r'^addclass/?$',views.addclass),
    url(r'^streams/on_publish/?$',views.on_publish),
    url(r'^streams/on_publish_done/?$',views.on_publish_done),
    url(r'^streams/on_play/?$',views.on_play),
    url(r'^streams/on_play_done/?$',views.on_play_done)
)
