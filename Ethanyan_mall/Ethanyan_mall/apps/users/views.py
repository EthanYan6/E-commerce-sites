import json
import random

import logging
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, GenericAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django_redis import  get_redis_connection
from users import constants
from users.serializers import UserSerializer, UserDetailSerializer, AddressSerializer, AddressTitleSerializer, \
    HistorySerializer, UserPasswordChangeSerializer
from users import serializers
from users.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from users.serializers import EmailSerializer
from goods.models import SKU
from goods.serializers import SKUSerializer
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from datetime import datetime
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken,jwt_response_payload_handler
logger = logging.getLogger('django')
from cart.utils import merge_cookie_cart_to_redis
# Create your views here.


# API: GET /accounts/(?P<username>\w+)/password/token/
class FindPasswdThirdView(APIView):
    def get(self,request,username):
        """
        1.用户收到短信并填写短信验证码；

        2.发送请求到后端，带上 account 和 sms_code;

        3.后端对参数进行校验；

        4.生成用于修改密码的 token，将 user_id 保存进去，返回 user_id 和 token

        """
        # 获取用户以及手机验证码
        user = User.objects.get(username=username)
        sms_code = request.GET.get('sms_code')
        # 从redis中获取真是的短信验证码
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % user.mobile)  # bytes
        if real_sms_code is None:
            return Response('短信验证码已经失效')
        # 对比短信验证码
        if real_sms_code.decode() != sms_code:
            return Response('短信验证码填写错误')
        # 生成用于修改密码的ｔｏｋｅｎ值．
        tjs = TJWSSerializer(settings.SECRET_KEY, 300)
        access_token = tjs.dumps({'user_id': user.id}).decode()
        return Response({'access_token':access_token,'user_id':user.id})


# GET /sms_codes/
class FindPasswdSecondView(APIView):
    def get(self,request):
        """
        1.前端发送请求，带上上一步生成的 access_token；

        2.在模型类中定义验证 token 的方法，使用 itdangerous 提供的方法进行反验证，取出存在token 中的手机号，进行判断是否在 60s 内，防止重复发送；

        3.生成短信验证码，存入 redis，使用异步 celery 发送短信；

        4.返回成功消息；

        """
        # 获取上一步的access_token
        access_token = request.GET.get('access_token')

        # 对获取到的ｔｏｋｅｎ进行解密校验．并且获取手机号
        serializer = TJWSSerializer(settings.SECRET_KEY,300)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        mobile = data.get('user')
        if mobile:
            # 判断给<mobile>60s内是否发送过短信
            redis_conn = get_redis_connection('verify_codes')

            send_flag = redis_conn.get('send_flag_%s' % mobile)  # None

            if send_flag:
                # 60秒内给<mobile>发送过短信了
                return Response({'message': '您点击过于频繁了，休息一会吧...'}, status=status.HTTP_403_FORBIDDEN)
            # 1.随机生成6位的数字作为短信验证码
            sms_code = '%06d' % random.randint(0, 999999)
            logger.info("短信验证码是 = %s" % sms_code)
            # 2.在redis中存储短信验证码内容，以'sms_<mobile>'为key，以验证码的内容为value
            # redis_conn = get_redis_connection('verify_codes')

            # redis_conn.set('<key>','<value>','<expires>')
            # redis_conn.setex('<key>','<expires>','<value>')
            # redis_conn.setex('sms_%s' % mobile,constants.SMS_CODE_REDIS_EXPIRES, sms_code)
            # redis_conn.setex('send_flag_%s' % mobile,constants.SEND_SMS_CODE_INTERVAL,1)

            # 创建redis管道对象
            pl = redis_conn.pipeline()

            # 向redis管道中添加命令
            pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
            pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

            # 一次性执行管道中的所有命令
            pl.execute()
            # 3.使用云通讯给mobile发送短信
            expires = constants.SMS_CODE_REDIS_EXPIRES // 60
            # 创建一个进程调用发送短信的函数
            from celery_tasks.sms.tasks import send_sms_code
            send_sms_code.delay(mobile, sms_code, expires)
            # 4.返回应答，短信发送成功
            return Response({'message': 'OK'})
        return Response({'message': '发送失败'})


# GET /accounts/(?P<username>\w+)/sms/token/
class FindPasswdOneView(APIView):

    def get(self,request,username):
        # 获取找回密码的用户
        # 因为我们之前重写过Django的认证后端类，所以认证方法username既可以传账号，又可以传入手机号。
        user = User.objects.get(username=username)

        image_code = request.GET.get('text')
        image_code_id = request.GET.get('image_code_id')
        redis_image = get_redis_connection('image_codes')
        try:
            real_image_code = redis_image.get("ImageCode_" + image_code_id)
            # 如果图片验证码取出成功,那么删除redis中的缓存.
            if real_image_code:
                real_image_code = real_image_code.decode()
                redis_image.delete("ImageCode_" + image_code_id)
        except Exception as e:

            return Response({'message': '获取图片验证码失败'}, status=status.HTTP_400_BAD_REQUEST)
        # 判断图片验证码是否已经过期
        if not real_image_code:
            # 过期
            return Response({'message': '图片验证码已过期'}, status=status.HTTP_400_BAD_REQUEST)
        # 进行图片验证码的校验
        if image_code.lower() != real_image_code.lower():
            # 验证码输入有误
            return Response({'message': '图片验证码输入有误'}, status=status.HTTP_400_BAD_REQUEST)


        # 将手机号加密
        tjs = TJWSSerializer(settings.SECRET_KEY, 300)
        access_token = tjs.dumps({'user': user.mobile}).decode()

        #　加密手机号
        per = user.mobile[0:3]
        back = user.mobile[-5:-1]
        sec = per + '****' + back


        # 做出响应.返回ａｃｃｅｓｓ＿ｔｏｋｅｎ和手机号
        return Response({'access_token': access_token,'mobile':sec})



# PUT /users/(?P<pk>\d+)/password/
class UserPasswordChangeView(GenericAPIView):
    serializer_class = UserPasswordChangeSerializer

    def post(self,request,pk):
        """
        1.在模型类中实现检验修改密码 token 的方法，取出 data，判断 user_id 是否一样；

        2.判断两次密码是否一样，判断是否是当前用户，返回数据；

        3.更新密码；

        4.返回重置密码成功信息。

        """
        user = User.objects.filter(id=pk).first()
        json_str = request.body
        json_str = json_str.decode()  # python3.6 无需执行此步
        req_data = json.loads(json_str)
        access_token = req_data.get('access_token')

        # 对ｔｏｋｅｎ进行解密
        sec = TJWSSerializer(settings.SECRET_KEY, 300)
        try:
            data = sec.loads(access_token)
        except BadData:
            return Response('非法请求')
        user_id = data.get('user_id')

        if user_id == int(pk):
            # 判断两次密码是否一致
            if req_data['password'] != req_data['password2']:
                return Response('两次密码不一样，请仔细检查一下下...')
            user.set_password(req_data['password'])
            user.save()
            return Response({'id':user_id,'username':user.username,'mobile':user.mobile})
        return Response('非法请求')
    def put(self,request,pk):
        """
        1.获取参数并校验，看原密码是否正确，两次密码是否一致。
        2.获取当前用户信息，更新到数据库。
        3.返回响应。
        """
        # 1.获取参数并校验，看原密码是否正确，两次密码是否一致。
        user = request.user

        # 2.获取参数并进行校验
        serializer = self.get_serializer(user,data = request.data)
        serializer.is_valid(raise_exception=True)

        # 3.保存修改地址的数据
        serializer.save()
        # 4.返回应答，修改成功
        return Response({'message':'OK'})

# POST /authorizations/
class UserAuthorizeView(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            # 调用合并购物车记录函数
            merge_cookie_cart_to_redis(request, user, response)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# POST /browse_histories/
class HistoryView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HistorySerializer

    # def post(self,request):
    #     """
    #     浏览记录保存
    #     1.获取sku_id并进行校验（sku_id必传，sku_id对应的商品是否存在）
    #     2.在redis中保存登录用户的浏览记录
    #     3.返回应答，浏览记录保存成功
    #     """
    #     # 1.获取sku_id并进行校验（sku_id必传，sku_id对应的商品是否存在）
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 2.在redis中保存登录用户的浏览记录
    #     serializer.save()
    #
    #     # 3.返回应答，浏览记录保存成功
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self,request):
        """
        浏览记录获取
        1.从redis中获取用户浏览的商品的id
        2.根据商品的id获取对应的数据
        3.将商品的数据序列化并返回
        """
        user = request.user

        # 1.从redis中获取用户浏览的商品的id
        # 获取redis链接
        redis_conn = get_redis_connection('histories')

        history_key = 'history_%s' % user.id

        # [b'<sku_id>',b'<sku_id>',....]
        sku_ids = redis_conn.lrange(history_key, 0, -1)


        # 2.根据商品的id获取对应的数据
        skus = []

        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id) # get(id='1')get(id='1')get(id=b'1')
            skus.append(sku)
        # 3.将商品的数据序列化并返回
        serializer = SKUSerializer(skus,many=True)
        return Response(serializer.data)

class AddressViewSet(CreateModelMixin,UpdateModelMixin,GenericViewSet):
    """地址视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    def get_queryset(self):
        """返回用户的地址查询集"""
        return self.request.user.addresses.filter(is_deleted=False)

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """
        request.user:获取登录的用户
        保存新增地址的数据
        1.接收参数并进行校验
        2.创建并保存新增地址数据
        3.返回应答，地址创建成功
        """
        # 用户地址数量是否超过上限
        count = request.user.addresses.filter(is_deleted = False).count()

        if count>constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message':'保存地址数据已经达到上限'},status=status.HTTP_400_BAD_REQUEST)
        # 调用 CreateModelMixin 扩展类中create方法
        return super().create(request)
    # GET /addresses/
    def list(self,request):
        """
        1.获取登录用户的所有地址数据
        2.将用户的地址数据序列化并返回
        """
        user = request.user
        # 1.获取登录用户的所有地址数据
        addresses = self.get_queryset()

        # 2.将用户的地址数据序列并返回
        serializer = self.get_serializer(addresses,many=True)
        return Response({
            'user_id':user.id,  # 用户id
            'default_address_id':user.default_address_id, # 默认地址id
            'limit':constants.USER_ADDRESS_COUNTS_LIMIT, # 地址数量上限
            'addresses':serializer.data,  # 地址数据
        })
    # PUT /addresses/(?P<pk>\d+)
    # def update(self, request, pk):
    #     """
    #     1.根据pk获取对应的地址数据
    #     2.获取参数并进行校验
    #     3.保存修改地址的数据
    #     4.返回应答，修改成功
    #     """
    #     # 1.根据pk获取对应的地址数据
    #     address = self.get_object()
    #     # 2.获取参数并进行校验
    #     serializer = self.get_serializer(address,data = request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 3.保存修改地址的数据
    #     serializer.save()
    #     # 4.返回应答，修改成功
    #     return Response(serializer.data)

    # DELETE /addresses/(?P<pk>\d+)/
    def destroy(self,request,pk):
        """
        1.根据pk获取对应的地址数据
        2.将地址删除
        3.返回应答
        """
        # 1.根据pk获取对应的地址数据
        address = self.get_object()
        # 2.将地址删除
        address.is_deleted = True
        address.save()
        # 3.返回应答
        return Response(status=status.HTTP_204_NO_CONTENT)

    # 设置默认地址
    # PUT /addresses/(?P<pk>\d+)/status/
    @action(methods=['put'],detail=True)
    def status(self,request,pk):
        """
        1.根据pk获取对应的地址数据
        2.将此地址设置为用户的默认地址
        3.返回应答
        """
        # 1.根据pk获取对应的地址数据
        address = self.get_object()

        # 2.将此地址设置为用户的默认地址
        # request.user.default_address = adress
        request.user.default_address_id = address.id
        request.user.save()
        # 3.返回应答
        return Response({'message':'OK'},status=status.HTTP_200_OK)

    # 设置地址标题
    # PUT /address/(?P<pk>\d+)/title/
    @action(methods=['put'],detail=True)
    def title(self,request,pk):
        """
        1.根据pk获取对应的地址数据
        2.获取title并进行校验
        3.设置地址标题
        4.返回应答
        """
        # 1.根据pk获取对应的地址数据
        address = self.get_object()
        # 2.获取title并进行校验
        serializer = AddressTitleSerializer(address,data=request.data)
        serializer.is_valid(raise_exception=True)
        # 3.设置地址标题
        serializer.save()
        # 4.返回应答
        return Response(serializer.data)




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