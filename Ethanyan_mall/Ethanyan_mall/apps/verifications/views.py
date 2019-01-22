from django.shortcuts import render
from rest_framework.views import APIView
# Create your views here.


# GET /sms_codes/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(APIView):
    """短信验证码"""
    pass
