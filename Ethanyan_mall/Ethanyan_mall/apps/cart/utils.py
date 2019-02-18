import base64
import pickle

from django_redis import get_redis_connection


def merge_cookie_cart_to_redis(request, user, response):
    """合并cookie中的购物车数据到redis数据库中"""
    # 获取cookie中的购物车数据
    cookie_cart = request.COOKIES.get('cart')

    if cookie_cart is None:
        # cookie购物车无数据，直接返回
        return

    cart_dict = pickle.loads(base64.b64encode(cookie_cart))

    if not cart_dict:
        # 字典为空，购物车无数据，直接返回
        return

    # 保存cookie购物车中添加的商品的id和对应的数量count，此字典中的数据在进行购物车记录合并时需要作为属性和值设置到redis hash中
    cart = {}

    # 保存cookie购物车中被勾选的商品的id,此列表中的元素在进行购物车记录合并时需要添加到redis set中
    cart_selected_add = []

    # 保存cookie购物车中未被勾选的商品的id，此列表中的元素在进行购物车记录合并是需要从redis set中移除
    cart_selected_remove = []

    for sku_id, count_selected in cart_dict.items():
        cart[sku_id] = count_selected['count']

        if count_selected['selected']:
            # 勾选
            cart_selected_add.append(sku_id)
        else:
            # 未勾选
            cart_selected_remove.append(sku_id)

    # 进行合并
    redis_conn = get_redis_connection('cart')

    # 向redis hash中合并商品的id和数量count
    cart_key = 'cart_%s' % user.id

    # 将cart字典中的key和value作为属性和值设置到redis的hash元素中，如果已经存在的属性和值会进行覆盖
    redis_conn.hmset(cart_key, cart)

    # 向redis set中合并勾选状态
    cart_selected_key = 'cart_selected_%s' % user.id

    if cart_selected_add:
        # 将cart_selected_add列表中商品的id添加到redis set 中
        redis_conn.sadd(cart_selected_key, *cart_selected_add)

    if cart_selected_remove:
        # 将cart_selected_remove列表中商品的id从redis set中移除
        redis_conn.srem(cart_selected_key, *cart_selected_remove)

    # 清除cookie的购物车数据
    response.delete_cookie('cart')