from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CASCADE
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

from Ethanyan_mall.utils.models import BaseModel
from users import constants
# Create your models here.
# 1.获取id为2的用户
# user = User.objects.get(id = 2)

# 获取user的默认地址
# user.default_address


class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')
    # openid = models.CharField(max_length=64,verbose_name='OpenID')
    email_active = models.BooleanField(default=False,verbose_name='用户邮箱验证状态')
    default_address = models.ForeignKey('Address',related_name='users',null=True,blank=True,
                                        on_delete=models.SET_NULL,verbose_name='默认地址')
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

# 1.获取id为1的地址
# address = Address.objects.get(id=1)

# 分别获取address地址所属的省、市和县
# address.province 所属省
# address.city     所属市
# address.district 所属县

# 获取id为200001的地区
# area = Area.objects.get(id=200001)
# 获取地址所属用户
# address.User.objects.get(id=2)

# 获取和user关联地址
# user.addresses.all()
# Address.objects.create(
#     # ...
#     province = '地区对象',
#     city = '地区对象',
#     district = '地区对象',
#     # ...
# )
class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User,on_delete=CASCADE,related_name='addresses',verbose_name='用户')
    title = models.CharField(max_length=20,verbose_name='地址名称')
    receiver = models.CharField(max_length=20,verbose_name='收货人')
    province = models.ForeignKey('areas.Area',related_name='province_address',on_delete=models.PROTECT,verbose_name='省')
    city = models.ForeignKey('areas.Area',related_name='city_address',on_delete=models.PROTECT,verbose_name='市')
    district = models.ForeignKey('areas.Area',related_name='district_address',on_delete=models.PROTECT,verbose_name='区')
    place = models.CharField(max_length=50,verbose_name='地址')
    mobile = models.CharField(max_length=11,verbose_name='手机')
    tel = models.CharField(max_length=20,null=True,blank=True,default='',verbose_name='固定电话')
    email = models.CharField(max_length=30,null=True,blank=True,default='',verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False,verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']

