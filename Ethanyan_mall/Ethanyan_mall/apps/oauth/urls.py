from django.conf.urls import url
from oauth import views
urlpatterns = [
    url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    url(r'^qq/user/$', views.QQAuthUserView.as_view()),
    url(r'^weibo/authorization/$',views.WeiboAuthURLLView.as_view()),
    url(r'^sina/user/$',views.WeiboOauthView.as_view()),
]