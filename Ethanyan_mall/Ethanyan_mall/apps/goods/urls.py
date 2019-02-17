from django.conf.urls import url
from goods import views

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/skus/$',views.SKUListView.as_view()),
]