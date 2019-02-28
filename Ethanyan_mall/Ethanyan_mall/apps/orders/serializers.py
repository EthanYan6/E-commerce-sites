from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderGoods, OrderInfo



class OrdersCommentCommitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderGoods
        fields = ('order','comment','is_anonymous','score','sku','is_commented')
        extra_kwargs = {
            'order': {
                'write_only': True,
            },

        }
    def update(self, instance, validated_data):
        instance.is_commented = True
        instance.is_anonymous = validated_data['is_anonymous']
        instance.score = validated_data['score']
        instance.comment = validated_data['comment']
        status = OrderInfo.ORDER_STATUS_ENUM['FINISHED']
        OrderInfo.objects.filter(order_id=int(validated_data['order'].order_id)).update(status=status)

        instance.save()
        return instance


class OrderSkuSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('default_image_url','name','id')

class OrderCommentSerializer(serializers.ModelSerializer):
    sku = OrderSkuSerializer()
    class Meta:
        model = OrderGoods
        fields = ('count', 'sku', 'price')


class OrderSKUSerializer(serializers.ModelSerializer):
    """订单结算商品的序列化器类"""
    count = serializers.IntegerField(label='结算商品数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'count')

class OrderSerializer(serializers.ModelSerializer):
    """订单创建的序列化器类"""
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)

        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True
            },
            'pay_method':{
                'write_only':True,
                'required':True
            }
        }

    def create(self, validated_data):
        """创建并保存订单的数据:(乐观锁)"""
        # 获取address和pay_method
        address = validated_data['address']
        pay_method = validated_data['pay_method']

        # 组织订单参数
        # 获取user
        user = self.context['request'].user

        # 订单id：年月日时分秒+下单用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%010d' % user.id

        # 订单商品总数量和实付款
        total_count = 0
        total_amount= 0

        # 运费10
        freight = Decimal(10)

        # 订单状态
        status = OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        redis_conn = get_redis_connection('cart')

        # 从redis购物车中获取用户所需要购买的商品id（redis set购物车中勾选的商品id）
        cart_selected_key = 'cart_selected_%s' % user.id

        # (b'<sku_id>',b'<sku_id>',..)
        sku_ids = redis_conn.smembers(cart_selected_key)

        # 从redis hash中获取用户购物车中添加的商品的id和对应数量count
        cart_key = 'cart_%s' % user.id

        cart_dict = redis_conn.hgetall(cart_key)

        with transaction.atomic():
            # with语句块下面的代码，凡是涉及到数据库操作的代码，在进行数据库操作时，都会放在同一个事务中
            # 设置事务保存点
            sid = transaction.savepoint()
            try:
                # 1.向订单基本信息表中添加一条记录
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user = user,
                    address = address,
                    total_count = total_count,
                    total_amount =total_amount,
                    freight = freight,
                    pay_method = pay_method,
                    status = status
                )

                # 2.订单中包含几个商品，就向订单商品表中添加几条记录


                for sku_id in sku_ids:
                    # 获取用户需要购买的该商品的数量
                    count = cart_dict[sku_id]
                    count = int(count)

                    for i in range(3):
                        # 根据sku_id获取商品的信息
                        # sku = SKU.objects.get(id=sku_id)
                        # select * from tb_sku where id=<sku_id>;
                        sku = SKU.objects.get(id=sku_id)


                        # 判断商品的库存
                        if count > sku.stock:
                            # 回滚事务到sid保存点
                            transaction.savepoint_rollback(sid)
                            raise serializers.ValidationError('商品的库存不足')

                        # 记录商品的原始库存
                        origin_stock = sku.stock
                        new_stock = origin_stock - count
                        new_sales = sku.sales + count

                        # 模拟订单并发的问题
                        print('user: %s time: %s stock: %s' % (user.id, i, origin_stock))
                        # import time
                        # time.sleep(10)
                        # 减少对应商品的库存，增加销量
                        # update tb_sku
                        # set stock=<new_stock>, sales = <ne_sales>
                        # where id = <sku_id> and stock=<origin_stock>;
                        # res:更新行数
                        res = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)

                        if res == 0:
                            if i == 2:
                                # 循环更新了3次,仍然更新失败,直接下单失败
                                # 回滚事务到sid保存点
                                transaction.savepoint_rollback(sid)
                                raise serializers.ValidationError('下单失败2')
                            # 更新失败,重新进行尝试
                            continue

                        # 向订单商品表中添加一条记录
                        OrderGoods.objects.create(
                            order = order,
                            sku = sku,
                            count=count,
                            price = sku.price
                        )

                        # 累加计算订单商品的总数量和总金额
                        total_count += count
                        total_amount += sku.price*count

                        # 如果更新成功,break跳出循环
                        break

                # 实付款
                total_amount +=freight
                order.total_count = total_count
                order.total_amount = total_amount
                order.save()
            except serializers.ValidationError:
                # 继续向外抛出捕获异常
                raise
            except Exception:
                # 回滚事务到sid保存点
                transaction.savepoint_rollback(sid)
                raise serializers.ValidationError('下单失败1')

        # 3.清除redis中对应的购物车记录
        pl = redis_conn.pipeline()
        pl.hdel(cart_key, *sku_ids)
        pl.srem(cart_selected_key, *sku_ids)
        pl.execute()

        return order


    def create_1(self, validated_data):
        """创建并保存订单的数据:(悲观锁)"""
        # 获取address和pay_method
        address = validated_data['address']
        pay_method = validated_data['pay_method']

        # 组织订单参数
        # 获取user
        user = self.context['request'].user

        # 订单id：年月日时分秒+下单用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%010d' % user.id

        # 订单商品总数量和实付款
        total_count = 0
        total_amount= 0

        # 运费10
        freight = Decimal(10)

        # 订单状态
        status = OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        redis_conn = get_redis_connection('cart')

        # 从redis购物车中获取用户所需要购买的商品id（redis set购物车中勾选的商品id）
        cart_selected_key = 'cart_selected_%s' % user.id

        # (b'<sku_id>',b'<sku_id>',..)
        sku_ids = redis_conn.smembers(cart_selected_key)

        # 从redis hash中获取用户购物车中添加的商品的id和对应数量count
        cart_key = 'cart_%s' % user.id

        cart_dict = redis_conn.hgetall(cart_key)

        with transaction.atomic():
            # with语句块下面的代码，凡是涉及到数据库操作的代码，在进行数据库操作时，都会放在同一个事务中
            # 设置事务保存点
            sid = transaction.savepoint()
            try:
                # 1.向订单基本信息表中添加一条记录
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user = user,
                    address = address,
                    total_count = total_count,
                    total_amount =total_amount,
                    freight = freight,
                    pay_method = pay_method,
                    status = status
                )

                # 2.订单中包含几个商品，就向订单商品表中添加几条记录


                for sku_id in sku_ids:
                    # 获取用户需要购买的该商品的数量
                    count = cart_dict[sku_id]
                    count = int(count)

                    # 根据sku_id获取商品的信息
                    # sku = SKU.objects.get(id=sku_id)
                    # select * from tb_sku where id=<sku_id>;
                    #  sku = SKU.objects.get(id=sku_id)

                    # select * from tb_sku where id = <sku_id> for update;
                    print('user: %s try get lock' % user.id)
                    sku = SKU.objects.select_for_update().get(id=sku_id)
                    print('user: %s get locked' % user.id)


                    # 判断商品的库存
                    if count > sku.stock:
                        # 回滚事务到sid保存点
                        transaction.savepoint_rollback(sid)
                        raise serializers.ValidationError('商品的库存不足')

                    # 模拟订单并发的问题
                    # print('user: %s' % user.id)
                    import time
                    time.sleep(10)
                    # 减少对应商品的库存，增加销量
                    sku.stock -= count
                    sku.sales += count
                    sku.save()

                    # 向订单商品表中添加一条记录
                    OrderGoods.objects.create(
                        order = order,
                        sku = sku,
                        count=count,
                        price = sku.price
                    )

                    # 累加计算订单商品的总数量和总金额
                    total_count += count
                    total_amount += sku.price*count

                # 实付款
                total_amount +=freight
                order.total_count = total_count
                order.total_amount = total_amount
                order.save()
            except serializers.ValidationError:
                # 继续向外抛出捕获异常
                raise
            except Exception:
                # 回滚事务到sid保存点
                transaction.savepoint_rollback(sid)
                raise serializers.ValidationError('下单失败')

        # 3.清除redis中对应的购物车记录
        pl = redis_conn.pipeline()
        pl.hdel(cart_key, *sku_ids)
        pl.srem(cart_selected_key, *sku_ids)
        pl.execute()

        return order
