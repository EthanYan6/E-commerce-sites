import re
from django_redis import get_redis_connection
from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """创建用户序列化器类"""
    # write_only表示该字段仅仅用于反序列化输入
    password2 = serializers.CharField(label='确认密码',write_only=True)
    sms_code = serializers.CharField(label='短信验证码',write_only=True)
    allow = serializers.CharField(label='同意协议',write_only=True)
    token = serializers.CharField(label='JWT token',read_only=True)

    class Meta:
        model = User
        fields = ('id','username','password','password2','sms_code','mobile','allow','token')
        extra_kwargs = {
            'username':{
                'min_length':5,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许5-20个字符的用户名',
                    'max_length':'仅允许5-20个字符的用户名',
                }
            },
            'password':{
                'write_only':True,
                'min_length':8,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许8-20个字符的密码',
                    'max_length':'仅允许8-20个字符的密码',
                }
            }
        }
    # 参数完整性，用户名是否存在，手机号格式，手机号是否存在，是否同意协议，两次密码是否一致，短信验证码是否正确
    def validate_mobile(self,value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机号格式错误')

        # 手机是否存在
        count = User.objects.filter(mobile=value).count()
        if count>0:
            raise serializers.ValidationError('此手机号已经注册过了，您是不是忘记了...')
        return value

    def validate_allow(self,value):
        """检验用户是否统一协议"""
        if value != 'true':
            raise serializers.ValidationError('照顾到您的权益，请同意用户协议..')
        return value

    def validate(self, attrs):
        """
        :param attrs: 字典，传入data数据
        :return:
        """
        # 判断两次密码是否一致
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一样，请仔细检查一下下...')

        # 判断手机短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = attrs['mobile']
        # bytes数据
        real_sms_code = redis_conn.get('sms_%s'%mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('短信验证码无效，请检查..')
        # 对比一下短信验证码，str格式
        if attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('再看看您的手机，验证码输错了哦...')
        return attrs

    def create(self, validated_data):
        """
        创建用户并保存新用户的信息
        validated_data：反序列化校验之后的数据

        """
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 创建新用户
        user = User.objects.create_user(**validated_data)

        # 由服务器生成一个jwt token字符串，保存用户的身份信息
        from rest_framework_jwt.settings import api_settings

        # 生成payload载荷
        jwt_payload_hanler = api_settings.JWT_PAYLOAD_HANDLER
        # 生成jwt token
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_hanler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)

        # 给user对象增加属性token，保存生成jwt token数据
        user.token = token
        return user
