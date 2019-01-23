from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.UsernameCountView.as_view())

]