

# Create your views here.
# GET /categories/(?P<category_id>\d+)/skus/
import json

import time
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from drf_haystack.viewsets import HaystackViewSet
from django.core import serializers
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from goods.models import SKU
from goods.serializers import SKUSerializer, SKUIndexSerializer, OrderGoodsSerializer
from orders.models import OrderGoods, OrderInfo
from users.models import User

# 2019年２月２８日写
# GET /orders/user/
class UserOrdersView(ListModelMixin,GenericViewSet):
    # 添加认证,登录用户才可以访问
    permission_classes = [IsAuthenticated]
    # 指定序列化器类
    serializer_class = OrderGoodsSerializer

    # 重写list方法
    def list(self, request, *args, **kwargs):
        # 获取登录用户
        user = request.user
        # 查询订单数据,按创建时间进行降序排列
        order = OrderInfo.objects.filter(user_id=user.id).order_by("-create_time")

        # 复制粘贴源代码中的分页功能代码
        queryset = self.filter_queryset(order)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 创建序列化器类对象
        serializer = self.get_serializer(order, many=True)

        data = {
            'count': len(order),
            'results': serializer.data
        }

        # 3.返回与用户相关的商品信息给前端
        return Response(data)







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