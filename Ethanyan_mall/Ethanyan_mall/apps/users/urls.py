from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from users import views

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',views.MobileCountView.as_view()),
    url(r'^users/$', views.UserView.as_view()),
    url(r'^authorizations/$',obtain_jwt_token),# 登录视图配置
    url(r'^user/$',views.UserDetailView.as_view()),
    url(r'^email/$',views.EmailView.as_view()),
    url(r'^emails/verification/$',views.EmailVerifyView.as_view()),

]