from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth.utils import OAuthQQ

# Create your views here.
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

