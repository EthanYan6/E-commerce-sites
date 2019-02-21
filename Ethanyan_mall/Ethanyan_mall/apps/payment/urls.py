from django.conf.urls import url
from payment import views

urlpatterns = [
    url(r'^orders/(?P<order_id>\d+)/payment/$', views.PaymentView.as_view()),
    url(r'^payment/status/$',views.PaymentStatusView.as_view()),

]