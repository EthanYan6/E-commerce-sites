import base64
import pickle

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart import constants
from cart.serializers import CartSerializer, CartSKUSerializer
from goods.models import SKU


class CartView(APIView):
    def perform_authentication(self, request):
        """让当前视图跳过DRF框架认证过程"""
        pass

    # POST /cart/
    def post(self,request):
        """
        购物车记录添加
        # 1.获取参数并进行校验（参数的完整性，sku_id商品是否存在，count是否大于商品库存
        # 2.保存用户的购物车记录
        #     2.1如果用户已登录，在redis中保存用户的购物车记录
        #     2.2如果用户未登录，在cookie中保存用户的购物车记录
        # 3.返回应答，购物车记录添加成功。
        """
        # 1.获取参数并进行校验（参数的完整性，sku_id商品是否存在，count是否大于商品库存
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取校验之后的数据
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']

        try:
            # 此代码会触发DRF框架认证过程，但是可以自己进行捕获处理
            user = request.user
        except Exception:
            user = None

        # 2.保存用户的购物车记录
        if user and user.is_authenticated:
        # 2.1如果用户已登录，在redis中保存用户的购物车记录
            # 获取链接对象
            redis_conn = get_redis_connection('cart')

            # hash:保存用户购物车添加的商品id和对应数量count
            cart_key = 'cart_%s' % user.id

            # 如果redis购物车已经添加该商品，数量需要进行累加
            redis_conn.hincrby(cart_key,sku_id,count)

            # set:保存用户购物车中被勾选的商品id
            cart_selected_key = 'cart_selected_%s' % user.id

            if selected:
                redis_conn.sadd(cart_selected_key,sku_id)
            return Response(serializer.validated_data,status=status.HTTP_201_CREATED)
        # 2.2如果用户未登录，在cookie中保存用户的购物车记录
        else:
            # 获取原始cookie购物车数据
            cookie_cart = request.COOKIES.get('cart')# None

            if cookie_cart:
                # {
                #     <sku_id>:{
                #     'count':'<count>',
                #     'selected':'<selected>'
                # },
                # ...
                # }
                cart_dict = pickle.loads(base64.b64encode(cookie_cart))
            else:
                cart_dict = {}
            # 保存购物车数据
            if sku_id in cart_dict:
                # 数量累加
                count += cart_dict[sku_id]['count']

            cart_dict[sku_id] = {
                'count':count,
                'selected':selected
            }

            # 3.返回应答，购物车记录添加成功。
            response = Response(serializer.validated_data,status=status.HTTP_201_CREATED)
            # 设置cookie购物车数据
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode() # str
            response.set_cookie('cart',cart_data,max_age=constants.CART_COOKIE_EXPIRES)
            return response
    # GET /cart/
    def get(self,request):
        """
        购物车记录获取
        1.获取用户的购物车记录
            1.1如果用户已登录，从redis中获取用户的购物车记录
            1.2如果用户未登录，从cookie中获取用户的购物车记录
        2.根据用户购物车中商品id获取对应商品的数据
        3.将购物车商品的数据序列化并返回
        """
        try:
            user = request.user
        except Exception:
            user = None
        # 1.获取用户的购物车记录
        if user and user.is_authenticated:
            # 1.1如果用户已登录，从redis中获取用户的购物车记录
            # 获取redis链接
            redis_conn = get_redis_connection('cart')

            # 从redis hash中获取用户购物车中添加的商品id和对应的数量count
            cart_key = 'cart_%s' % user.id
            # {
            #     b'<sku_id>': b'<count>',
            #     ...
            # }
            cart_redis = redis_conn.hgetall(cart_key)

            # 从redis set中获取用户购物车中勾选的商品id
            cart_selected_key = 'cart_selected_%s' % user.id

            # (b'<sku_id>',...)
            cart_selected_redis = redis_conn.smembers(cart_selected_key)

            cart_dict = {}
            for sku_id,count in cart_redis.items():
                cart_dict[int(sku_id)] = {
                    'count':int(count),
                    'selected':sku_id in cart_selected_redis
                }
        else:
            # 1.2如果用户未登录，从cookie中获取用户的购物车记录
            # 获取cookie中的购物车数据
            cookie_cart = request.COOKIES.get('cart')

            if cookie_cart:
                # 解析cookie中购物车数据
                # {
                #     '<sku_id>': {
                #         'count': '<count>',
                #         'selected': '<selected>'
                #     },
                #     ...
                # }
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                cart_dict = {}

        # 2.根据用户购物车中商品id获取对应商品的数据
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in = sku_ids)

        for sku in skus:
            # 给sku对象增加属性count和selected，分别保存该商品在购物车中添加的数量和勾选状态
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']


        # 3.将购物车商品的数据序列化并返回
        serializer = CartSKUSerializer(skus,many=True)
        return Response(serializer.data)