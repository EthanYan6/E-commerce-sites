from django.contrib import admin
from goods import models
# Register your models here.

class SKUAdmin(admin.ModelAdmin):
    """SKU模型类Admin管理类"""
    def save_model(self, request, obj, form, change):
        # 数据保存
        obj.save()

        # 附加逻辑：发出重新生成静态详情页面的任务消息
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html(obj.id)


class SKUSpecificationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # 数据保存
        obj.save()

        # 附加逻辑：发出重新生成静态详情页面的任务消息
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self, request, obj):
        # 数据删除
        sku_id = obj.sku.id
        obj.delete()

        # 附加逻辑：发出重新生成静态详情页面的任务消息
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


class SKUImageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # 数据保存
        obj.save()

        # 附加逻辑：发出重新生成静态详情页面的任务消息
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

        # 附加代码：设置SKU默认图片
        sku = obj.sku
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url
            sku.save()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)

admin.site.register(models.GoodsCategory)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
admin.site.register(models.SKUImage, SKUImageAdmin)
