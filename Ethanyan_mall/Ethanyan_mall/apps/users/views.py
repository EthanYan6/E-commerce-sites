from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users import constants
from users.serializers import UserSerializer, UserDetailSerializer, AddressSerializer
from users import serializers
from users.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin
from users.serializers import EmailSerializer
# Create your views here.

class AddressViewSet(CreateModelMixin,GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """
        request.user:获取登录的用户
        保存新增地址的数据
        1.接收参数并进行校验
        2.创建并保存新增地址数据
        3.返回应答，地址创建成功
        """
        # 用户地址数据是否超过上限
        count = request.user.addresses.filter(is_deleted = False).count()

        if count>constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message':'保存地址数据已经达到上限'},status=status.HTTP_400_BAD_REQUEST)
        # 调用 CreateModelMixin 扩展类中create方法
        return super().create(request)

# PUT /emails/verification/?token=<加密信息>
class EmailVerifyView(APIView):
    def put(self,request):
        """
        用户邮箱验证
        1.获取token（加密用户信息）并进行校验（token必传，token是否有效）
        2.设置用户的邮箱验证标记True
        3.返回应答，邮箱验证成功
        """
        # 1.获取token（加密用户信息）并进行校验（token必传，token是否有效）
        token = request.query_params.get('token')

        if token is None:
            return Response({'message':'缺少token参数'},status=status.HTTP_400_BAD_REQUEST)
        # token是否有效
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message':'无效的token数据'},status=status.HTTP_400_BAD_REQUEST)

        # 2.设置用户的邮箱验证标记True
        user.email_active = True
        user.save()

        # 3.返回应答，邮箱验证成功
        return Response({'message':'OK'})

# GET /user/
# class UserDetailView(RetrieveModelMixin,GenericAPIView):
class UserDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer
    def get_object(self):
        """返回登录用户对象"""
        # self.request:request请求对象
        return  self.request.user
    # def get(self,request):
    #     return self.retrieve(request)
    # def get(self,request):
    #     """
    #     获取登录用户基本信息
    #     1.获取登录用户
    #     2.将登录用户对象序列化并返回
    #     """
    #     # request.user
    #     # 如果用户已经认证，request.user就是登录用户对象
    #     # 如果用户没有认证，request.user就是一个匿名类的对象
    #     # 1.获取登录用户
    #     user = request.user
    #     # 2.将登录用户对象序列化并返回
    #     serializer = self.get_serializer(user)
    #     return Response(serializer.data)


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
# POST /users/
# url(r'^users/$', views.UserView.as_view()),
class UserView(CreateAPIView):
    """用户注册"""
    serializer_class = UserSerializer

# 第二种方法：
# class UserView(GenericAPIView):
#     # 指定视图所使用的序列化器类
#     serializer_class = UserSerializer
#
#     def post(self,request):
#         """
#         注册用户信息的保存（创建新用户）：
#         1.获取参数并进行校验（参数完整性，用户名不能全部为数字，用户名是否存在，手机号格式，手机号是否存在，是否同意协议，两次密码是否一致，短信验证码是否正确
#         2.创建并保存新用户的信息
#         3.返回应答，注册成功
#         :param request:
#         :return:
#         """
#         # 1.获取参数并进行校验（参数完整性，用户名是否存在，手机号格式，手机号是否存在，是否同意协议，两次密码是否一致，短信验证码是否正确
#         # 返回序列化器类对象
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         # 2.创建并保存新用户的信息
#         serializer.save()
#         # 3.返回应答，注册成功
#         return Response(serializer.data,status=status.HTTP_201_CREATED)

# PUT /email/
# class EmailView(GenericAPIView):
class EmailView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer
    def get_object(self):
        """返回登录用户"""
        return self.request.user
    # def put(self,request):
    #     """
    #     保存登录用户的邮箱
    #     1.获取参数并进校校验（email必传，邮箱格式）
    #     2.设置登录用户的邮箱并给邮箱发送验证邮件
    #     3.返回应答，邮箱设置成功
    #     """
    #     # 1.获取参数并进校校验（email必传，邮箱格式）
    #     user = request.user
    #     serializer = self.get_serializer(user,data=request.data)
    #     serializer.is_vaild(raise_exception=True)
    #     # 2.设置登录用户的邮箱并给邮箱发送验证邮件
    #     serializer.save()
    #     # 3.返回应答，邮箱设置成功
    #     return Response(serializer.data)