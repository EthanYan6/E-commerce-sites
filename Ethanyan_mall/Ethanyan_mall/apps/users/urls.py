from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^set_session/$',views.set_session),
    url(r'^get_session/$',views.get_session),

]