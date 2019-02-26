from django.conf.urls import url
from verifications import views
urlpatterns = [
    url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
    url(r'^image_codes/(?P<image_code_id>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/$',views.ImageCodeView.as_view()),
]