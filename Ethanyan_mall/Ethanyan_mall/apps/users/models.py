from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from users import constants
# Create your models here.



class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')
    # openid = models.CharField(max_length=64,verbose_name='OpenID')
    email_active = models.BooleanField(default=False,verbose_name='用户邮箱验证状态')
    class Meta:
        # 指明数据库表名
        db_table = 'tb_users'
        # 在admin站点中显示的名称
        verbose_name = '用户'
        # 显示的复数名称
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        """生成用户的邮箱验证链接地址"""
        # 组织数据
        data = {
            'id':self.id,
            'email':self.email
        }
        # 进行加密
        serializer = TJWSSerializer(secret_key=settings.SECRET_KEY,expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        token = serializer.dumps(data).decode()

        # 拼接链接地址
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url
    @staticmethod
    def check_verify_email_token(token):
        """
        token:加密用户信息
        """
        # 进行解密
        serializer = TJWSSerializer(secret_key=settings.SECRET_KEY)

        try:
            data = serializer.loads(token)
        except BadData:
            # 解密失败
            return None
        else:
            # 解密成功
            id = data.get('id')
            email = data.get('email')

            # 查询用户
            try:
                user = User.objects.get(id=id,email=email)
            except User.DoesNotExist:
                return None
            else:
                return user
