import re
from django.contrib.auth.backends import ModelBackend
from users.models import User

def jwt_response_payload_handler(token,user=None,request=None):
    """
    自定义jwt扩展登录视图的响应数据函数

    """
    return {
        'user_id':user.id,
        'username':user.username,
        'token':token
    }

def get_user_by_account(account):
    """
    :param account: 用户名或手机号
    :return: User对象 或者 None
    """
    try:
        if re.match(r'^1[3-9]\d{9}$',account):
            # 根据手机号查询用户
            user = User.objects.get(mobile=account)
        else:
            # 根据用户名查询用户
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        # 用户不存在
       return None
    else:
        return user


# 自定义django认证后端类
class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        :param request:
        :param username: 用户名或者手机号
        :param password: 密码
        :param kwargs:
        :return:
        """
        # 1.根据用户名或这手机号查询用户
        user = get_user_by_account(username)

        # 2.校验用户密码，如果密码登录，返回User
        if user and user.check_password(password):
            # 账户密码正确
            return user

