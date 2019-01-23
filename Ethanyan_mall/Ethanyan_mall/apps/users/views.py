from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
# Create your views here.


# GET /usernames/(?P<username>\w{5,20})/count/
class UsernameCountView(APIView):
    def get(self,request,username):
        """
        获取用户名数量
        1.根据用户名查询数据库，获取查询结果数量
        2.返回用户名数量
        :param request:
        :param username:
        :return:
        """
        # 1.根据用户名查询数据库，获取查询结果数量
        count = User.objects.filter(username=username).count()
        # 2.返回用户名数量
        res_data = {
            "username":username,
            "count":count
        }
        return Response(res_data)

# GET /mobiles/(?P<mobile>1[3-9]\d{9})/count/
class MobileCountView(APIView):
    def get(self,request,mobile):
        """
        获取用户名数量
        1.根据手机号查询数据库，获取查询结果数量
        2.返回手机号数量
        :param request:
        :param username:
        :return:
        """
        # 1.根据手机号查询数据库，获取查询结果数量
        count = User.objects.filter(mobile=mobile).count()
        # 2.返回手机号数量
        res_data = {
            "mobile":mobile,
            "count":count
        }
        return Response(res_data)
