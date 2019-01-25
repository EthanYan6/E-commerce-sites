from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from oauth.exceptions import QQAPIError
from oauth.models import OAuthQQUser
from oauth.utils import OAuthQQ

# Create your views here.
# GET /oauth/qq/user/?code=<code>
class QQAuthUserView(APIView):
    def get(self,request):
        """
        获取QQ登录用户的openid并处理
        1.获取code并校验
        2.获取QQ登录用户的openid
            2.1根据code请求QQ服务器获取access_token
            2.2根据access_token请求QQ服务器获取openid
        3.根据openid判断是否绑定过本网站的用户
            3.1如果已经绑定，直接身处jwt token
            3.2如果未绑定，将openid加密并返回
        """
        # 1.获取code并校验
        code = request.query_params.get('code') # None
        if code is None:
            return Response({'message':'缺少code参数'},status=status.HTTP_400_BAD_REQUEST)

        # 2.获取QQ登录用户的openid
        oauth = OAuthQQ()
        try:
            # 2.1根据code请求QQ服务器获取access_token
            access_token = oauth.get_access_token(code)
            # 2.2根据access_token请求QQ服务器获取openid
            openid = oauth.get_openid(access_token)
        except QQAPIError:
            return Response({'message':'QQ服务器异常'},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # 3.根据openid判断是否绑定过本网站的用户
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 3.2如果未绑定，将openid加密并返回
            secret_openid = oauth.generate_save_user_token(openid)
            return Response({'access_token':secret_openid})
        else:
            # 3.1如果已经绑定，直接身处jwt token
            user = qq_user.user

            # 由服务器生成一个jwt token字符串，保存用户的身份信息
            from rest_framework_jwt.settings import api_settings

            # 生成payload载荷
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            # 生成jwt token
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            # 生成jwt token
            token = jwt_encode_handler(payload)

            # 组织响应数据并返回
            response_data = {
                'user_id':user.id,
                'username':user.username,
                'token':token
            }
            return Response(response_data)


# GET /oauth/qq/authorization/?next=<登录之后跳转页面的地址>
class QQAuthURLView(APIView):
    def get(self,request):
        """
        获取QQ登录网址
        1.获取next（可以不传）
        2.阻止qq登录网址和参数
        3.返回qq登录网站
        """
        # 1.获取next（可以不传）
        next = request.query_params.get('next','/')
        # 2.阻止qq登录网址和参数
        oauth = OAuthQQ(state=next)
        login_url = oauth.get_login_url()
        # 3.返回qq登录网站
        return Response({'login_url':login_url})

