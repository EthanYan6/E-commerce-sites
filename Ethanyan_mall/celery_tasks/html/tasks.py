# 封装生成商品静态详情页面的任务函数
from celery_tasks.main import celery_app

import os
from django.conf import settings

from goods.models import SKU
from goods.utils import get_categories


@celery_app.task(name='generate_static_sku_detail_html')
def generate_static_sku_detail_html(sku_id):
    """生成指定商品的静态详情页面"""
    # 1.从数据库中查询详情页所需数据
    # 商品分类菜单
    # 我们将具体的代码封装成了一个函数，直接进行调用即可
    categories = get_categories()

    # 获取当前sku的信息
    sku = SKU.objects.get(id=sku_id)
    #  获取当前商品的图片，然后进行获取保存
    sku.images = sku.skuimage_set.all()

    # 找到和sku关联的频道
    # 找到和sku关联的spu对象
    goods = sku.goods
    # 先找到spu关联分类的一级分类，然后再找到和一级分类关联的频道，最终只有一个，我们取第一个就行了
    goods.channel = goods.category1.goodschannel_set.all()[0]

    # 构建当前商品的规格键
    # sku_key = [规格1参数id， 规格2参数id， 规格3参数id, ...]
    sku_specs = sku.skuspecification_set.order_by('spec_id')
    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    # 获取当前商品的所有SKU
    skus = goods.sku_set.all()

    # 构建不同规格参数（选项）的sku字典
    # spec_sku_map = {
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     ...
    # }
    spec_sku_map = {}
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.skuspecification_set.order_by('spec_id')
        # 用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    # 获取当前商品的规格信息
    # specs = [
    #    {
    #        'name': '屏幕尺寸',
    #        'options': [
    #            {'value': '13.3寸', 'sku_id': xxx},
    #            {'value': '15.4寸', 'sku_id': xxx},
    #        ]
    #    },
    #    {
    #        'name': '颜色',
    #        'options': [
    #            {'value': '银色', 'sku_id': xxx},
    #            {'value': '黑色', 'sku_id': xxx}
    #        ]
    #    },
    #    ...
    # ]
    specs = goods.goodsspecification_set.order_by('id')
    # 若当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(specs):
        return
    for index, spec in enumerate(specs):
        # 复制当前sku的规格键
        key = sku_key[:]
        # 该规格的选项
        options = spec.specificationoption_set.all()
        for option in options:
            # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))

        spec.options = options

    # 2.使用模板文件detail.html，进行模板渲染，获取渲染之后的html内容
    context = {
        'categories': categories,
        'goods': goods,
        'specs': specs,
        'sku': sku
    }

    # 2.1加载模板：指定使用的模板文件获取一个模板对象
    from django.template import loader
    temp = loader.get_template('detail.html')

    # 2.2模板渲染:获取替换之后html页面内容
    res_html = temp.render(context)

    # 3.将渲染之后的html内容保存成一个静态页面
    save_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR,'goods/%s.html' % sku_id)

    with open(save_path,'w') as f:
        f.write(res_html)
