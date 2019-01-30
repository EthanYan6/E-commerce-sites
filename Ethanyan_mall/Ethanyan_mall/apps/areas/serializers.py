from rest_framework import serializers
from areas.models import Area

class AreaSerializer(serializers.ModelSerializer):
    """地区序列化器类"""
    class Meta:
        model = Area
        fields = ('id','name')

class SubAreaSerializer(serializers.ModelSerializer):
    """地区序列化器类"""
    subs = AreaSerializer(label='下级地区',many=True)
    class Meta:
        model = Area
        fields = ('id','name','subs')