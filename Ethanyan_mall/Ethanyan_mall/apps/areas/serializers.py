from rest_framework import serializers
from areas.models import Area

class AreaSerializer(serializers.ModelSerializer):
    """地区序列化器类"""
    class Meta:
        model = Area
        fields = ('id','name')
