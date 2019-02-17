from rest_framework import serializers


from goods.models import SKU

class CartSerializer(serializers.Serializer):
    """购物车序列化器类"""
    sku_id = serializers.IntegerField(label='商品id',min_value=1)
    count = serializers.IntegerField(label='数量',min_value=1)
    selected = serializers.BooleanField(label='勾选状态',default=True)

    def validate(self, attrs):
        # sku_id商品是否存在
        sku_id = attrs['sku_id']

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        # count是否大于商品库存
        count = attrs['count']

        if count > sku.stock:
            raise serializers.ValidationError('商品库存不足')

        return attrs