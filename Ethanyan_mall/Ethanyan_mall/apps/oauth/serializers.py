import base64
import os

from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OAuthQQUser
from oauth.utils import OAuthQQ
from users.models import User


class QQAuthUserSerializer(serializers.ModelSerializer):
    """qq用户绑定数据的序列化器类"""
    sms_code = serializers.CharField(label='短信验证码',write_only=True)
    access_token = serializers.CharField(label='加密openid',write_only=True)
    token = serializers.CharField(label='JWT token',read_only=True)
    mobile = serializers.RegexField(label='手机号',regex=r'^1[3-9]\d{9}$',write_only=True)

    class Meta:
        model = User
        fields = ('id','username','mobile','password','sms_code','access_token','token')

        extra_kwargs = {
            'username':{
                'read_only':True
            },
            'password':{
                'write_only':True,
                'min_length':8,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许8-20个字符的密码',
                    'max_length':'仅允许8-20个字符的密码'

                }
            }
        }
    # 参数完整性，手机号格式，短信验证码是否正确，access_token是否有效
    def validate(self,attrs):
        # access_token是否有效
        access_token = attrs['access_token']
        openid = OAuthQQ.check_save_user_token(access_token)
        if openid is None:
            # 解密失败
            raise serializers.ValidationError('无效的access_token')
        # 向attrs中添加openid
        attrs['openid'] = openid

        # 短信验证码是否正确
        mobile = attrs['mobile']

        # 从redis中获取真是的短信验证码
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile) # bytes
        if real_sms_code is None:
            raise serializers.ValidationError('短信验证码已经失效')
        # 对比短信验证码
        sms_code = attrs['sms_code'] # str
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码填写错误')
        # 如果手机号已经注册，需要校验密码是否正确
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 手机号没注册
            user = None
        else:
            # 手机号已经注册
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')
        # 向attrs中添加User
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        # 如果手机号没有注册，先创建一个新用户
        user = validated_data['user']

        if user is None:
            mobile = validated_data['mobile']
            password = validated_data['password']
            # 随机生成用户名
            username = base64.b64encode(os.urandom(9)).decode()
            user = User.objects.create_user(username=username,mobile=mobile,password=password)
        # 给类视图对象增加属性User，保存绑定用户的数据
        self.context['view'].user = user
        # 保存绑定用户数据
        openid = validated_data['openid']
        OAuthQQUser.objects.create(
            user=user,
            openid=openid
        )
        # 有服务器产生一个jwt token字符串，保存用户的身份信息
        from rest_framework_jwt.settings import api_settings

        # 生成payload载荷
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # 生成jwt token
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)
        # 给User增加属性token，保存jwt token
        user.token = token
        return user

