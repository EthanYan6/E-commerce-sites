from django.conf.urls import url

from orders import views

urlpatterns = [
    url(r'^orders/settlement/$', views.OrderSettlmentView.as_view()),
]