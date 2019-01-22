from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')

    class Meta:
        # 指明数据库表名
        db_table = 'tb_users'
        # 在admin站点中显示的名称
        verbose_name = '用户'
        # 显示的复数名称
        verbose_name_plural = verbose_name
