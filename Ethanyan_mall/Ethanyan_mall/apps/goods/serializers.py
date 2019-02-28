import time
from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers

from goods.models import SKU
from goods.search_indexes import SKUIndex
from orders.models import OrderGoods, OrderInfo


class SKUSerializer(serializers.ModelSerializer):
    """商品序列化类"""
    class Meta:
        model = SKU
        fields = ('id','name','price','default_image_url','comments')


class SKUIndexSerializer(HaystackSerializer):
    """
    搜索结果的序列化器类
    """
    object = SKUSerializer(label='商品',read_only=True)

    class Meta:
        # 指定索引列
        index_classes = [SKUIndex]
        fields = ('text','object')


# 用来序列化和订单有关的商品信息
class OrderSkuSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('default_image_url','name')


#用来序列化订单商品信息
class GoodsInfoSerializer(serializers.ModelSerializer):
    sku = OrderSkuSerializer()
    count = serializers.IntegerField(label='下单数量',read_only=True)
    price = serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)

    class Meta:
        model = OrderGoods
        fields = ('count','sku','price')



class OrderGoodsSerializer(serializers.ModelSerializer):
    '''订单基本信息序列化器类'''
    skus = GoodsInfoSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = ('create_time','order_id','total_amount','pay_method','status','skus','freight')



