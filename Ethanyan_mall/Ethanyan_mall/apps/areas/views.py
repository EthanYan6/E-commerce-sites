from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from areas.models import Area
from areas.serializers import AreaSerializer

# Create your views here.
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