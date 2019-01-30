from django.conf.urls import url

from areas import views

urlpatterns = [
    # url(r'^areas/$',views.AreasView.as_view()),
    # url(r'^areas/(?P<pk>\d+)/$',views.SubAreasView.as_view()),
]

# 路由router
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('areas',views.AreasViewSet,base_name='areas')
urlpatterns += router.urls