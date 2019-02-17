from django.shortcuts import render

# Create your views here.
# GET /categories/(?P<category_id>\d+)/skus/
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from goods.models import SKU
from goods.serializers import SKUSerializer


class SKUListView(ListAPIView):
    serializer_class = SKUSerializer
    # queryset = SKU.objects.filter(category_id=category_id)

    def get_queryset(self):
        """返回第三级分类id获取SKU商品的数据"""
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id)

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