from django.shortcuts import render
from rest_framework.views import APIView
# Create your views here.


# GET /sms_codes/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(APIView):
    """短信验证码"""
    def get(self,request,mobile):
        """
        获取短信验证码
        1.随机生成6位的数字作为短信验证码
        2.在redis中存储短信验证码内容，以'sms_<mobile>'为key，以验证码的内容为value
        3.使用云通讯给mobile发送短信
        4.返回应答，短信发送成功
        """
        # 1.随机生成6位的数字作为短信验证码
        # 2.在redis中存储短信验证码内容，以'sms_<mobile>'为key，以验证码的内容为value
        # 3.使用云通讯给mobile发送短信
        # 4.返回应答，短信发送成功
