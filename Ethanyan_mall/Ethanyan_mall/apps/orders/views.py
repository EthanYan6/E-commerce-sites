from django.shortcuts import render
from decimal import Decimal
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from goods.models import SKU
from orders.serializers import OrderSKUSerializer
# Create your views here.


# GET /orders/settlement/
class OrderSettlmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        """
        获取订单结算商品的数据：
        1.从redis购物车记录获取登录用户所要结算商品的id和对应数量count
        2.根据商品的id获取对应商品的信息并组织运费
        3.将商品的数据序列化并返回
        """
        user = request.user

        # 1.从redis购物车记录获取登录用户所要结算商品的id和对应数量count
        redis_conn = get_redis_connection('cart')

        # 从redis  set中获取用户购物车勾选的商品的id
        cart_selected_key = 'cart_selected_%s' % user.id

        # Set(b'<sku_id>',b'<sku_id>',...)
        sku_ids = redis_conn.smembers(cart_selected_key)

        # 从redis hash中获取用户购物车商品的id和对应数量count
        cart_key = 'cart_%s' % user.id

        redis_cart = redis_conn.hgetall(cart_key)

        cart = {}

        for sku_id, count in redis_cart.items():
            cart[int(sku_id)] = int(count)

        # 2.根据商品的id获取对应商品的信息并组织运费
        skus = SKU.objects.filter(id__in = sku_ids)

        for sku in skus:
            # 获取该商品所要结算的数量，给sku对象增加count属性并保存结算的数量
            sku.count = cart[sku.id]

        # 组织运费： 10
        freight = Decimal(10)

        # 3.将商品的数据序列化并返回
        serializer = OrderSKUSerializer(skus, many=True)

        response_data = {
            'freight':freight,
            'skus':serializer.data
        }

        return Response(response_data)

