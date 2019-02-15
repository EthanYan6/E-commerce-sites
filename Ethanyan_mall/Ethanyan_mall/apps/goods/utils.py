from collections import OrderedDict

from goods.models import GoodsChannel

def get_categories():
    """
    获取商城商品分类菜单
    :return: 菜单字典
    """
    # 商品频道及分类菜单
    # 使用有序字典保存类别的顺序
    # 商品频道及分类菜单
    # 使用有序字典保存类别的顺序
    # categories = {
    # 三级菜单中，一级分类对应的是组，里面包含的是频道。
    #     1: { # 组1
    #         'channels': [{'id':, 'name':, 'url':},{}, {}...], # 频道
    #         'sub_cats': [{'id':, 'name':, 'sub_cats':[{},{}]}, {}, {}, ..] # 二级分类里面的sub_cats是三级分类
    #     },
    #     2: { # 组2
    #
    #     }
    # }

    categories = OrderedDict()  # 有序字典
    # 查询所有频道信息，按照 组id 和 组内的展示顺序 进行排序
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 遍历所有的频道
    for channel in channels:
        # 找到当前频道所在的组，拿到组id
        group_id = channel.group_id  # 当前组
        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}
        # 找到频道的一级分类
        cat1 = channel.category  # 当前频道的类别

        # 追加当前频道
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # 构建当前类别的子类别
        # 找到一级分类的二级分类
        for cat2 in cat1.goodscategory_set.all():
            # 用来记录二级分类下面的三级分类
            cat2.sub_cats = []
            for cat3 in cat2.goodscategory_set.all():
                # 将三级分类添加到二级分类中
                cat2.sub_cats.append(cat3)
            # 将二级分类添加到一级分类中。
            categories[group_id]['sub_cats'].append(cat2)
    return categories
