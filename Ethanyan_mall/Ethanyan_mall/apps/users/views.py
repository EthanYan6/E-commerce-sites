
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
from users.models import User

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
