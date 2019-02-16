from rest_framework import serializers

from goods.models import SKU



class SKUSerializer(serializers.ModelSerializer):
    """商品序列化类"""
    class Meta:
        model = SKU
        fields = ('id','name','price','default_image_url','comments')

