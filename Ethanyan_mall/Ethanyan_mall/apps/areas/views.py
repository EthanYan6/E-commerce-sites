from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area
from areas.serializers import AreaSerializer, SubAreaSerializer


# Create your views here.
# list
# retrieve
class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    """地区视图集"""
    def get_serializer_class(self):
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer
    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

# GET /areas/
class AreasView(ListAPIView):
    serializer_class = AreaSerializer
    # 指定当前视图所使用的查询集
    queryset = Area.objects.filter(parent=None)

    # def get(self,request):
    #     """
    #     获取所有省级地区的信息
    #     1.查询获取所有省级地区的信息
    #     2.将省级地区的信息序列化并返回
    #     """
    #     # 1.查询获取所有省级地区的信息
    #     areas = self.get_queryset()
    #     # 2.将省级地区的信息序列化并返回
    #     serializer = self.get_serializer(areas,many=True)
    #     return Response(serializer.data)

# GET /areas/(?P<pk>\d+)/
class SubAreasView(RetrieveAPIView):
    serializer_class = SubAreaSerializer
    queryset = Area.objects.all()

    # get_object():从查询集获取指定的对象，默认根据pk进行查询
    # def get(self,request,pk):
    #     """
    #     获取指定地区的信息
    #     1.根据pk获取指定地区的信息
    #     2.将指定地区的信息序列化并返回
    #     """
    #     # 1.根据pk获取指定地区的信息
    #     area = self.get_object()
    #     # 2.将指定地区的信息序列化并返回
    #     serializer = self.get_serializer(area)
    #     return Response(serializer.data)


