from django.shortcuts import render

# Create your views here.
# GET /categories/(?P<category_id>\d+)/skus/
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView

from goods.models import SKU
from goods.serializers import SKUSerializer, SKUIndexSerializer


class UserCenterOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        pass




# GET /skus/search/?text=<搜索关键字>
class SKUSearchViewSet(HaystackViewSet):
    # 指定索引类对应模型类
    index_models = [SKU]

    # 指定搜索结果序列化时所使用的序列化器类
    # s搜索结果中每个对象都包含两个属性：
    # text：索引字段的内容
    # object：从数据库中搜索出模型对象
    serializer_class = SKUIndexSerializer


class SKUListView(ListAPIView):
    serializer_class = SKUSerializer
    # queryset = SKU.objects.filter(category_id=category_id)

    def get_queryset(self):
        """返回第三级分类id获取SKU商品的数据"""
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id)

    # 排序
    filter_backends = [OrderingFilter]
    # 指定排序字段
    ordering_fields = ('create_time','price','sales')


    # def get(self,request,catefory_id):
    #     """
    #     self.kwargs:字典，保存从url地址中提取的所有命名参数
    #     根据第三级分类id获取分类SKU商品的数据：
    #     1. 根据category_id获取分类SKU商品的数据。
    #     2. 将商品的数据序列化并返回
    #     """
    #     # 1.根据category_id获取分类SKU商品的数据。
    #     # skus = SKU.objects.filter(category_id=category_id)
    #     skus = self.get_queryset()
    #
    #     # 2.将商品的数据序列化并返回
    #     serializer = self.get_serializer(skus,many=True)
    #     return Response(serializer.data)