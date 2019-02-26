import logging
import random

from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from Ethanyan_mall.utils.captcha.captcha import captcha
from verifications import constants

logger = logging.getLogger('django')

# GET /image_codes/(?P<image_code_id>\d+)/
class ImageCodeView(APIView):
    """图片验证码"""
    def get(self,request,image_code_id):
        # 生成验证码
        name, text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('image_codes')
        redis_conn.setex('ImageCode_' + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        response = HttpResponse(image,content_type='image/jpg')
        return response



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

        # 判断给<mobile>60s内是否发送过短信
        redis_conn = get_redis_connection('verify_codes')

        send_flag = redis_conn.get('send_flag_%s' % mobile) # None

        if send_flag:
            # 60秒内给<mobile>发送过短信了
            return Response({'message':'您点击过于频繁了，休息一会吧...'},status=status.HTTP_403_FORBIDDEN)
        # 1.随机生成6位的数字作为短信验证码
        sms_code = '%06d' % random.randint(0,999999)
        logger.info("短信验证码是 = %s"%sms_code)
        # 2.在redis中存储短信验证码内容，以'sms_<mobile>'为key，以验证码的内容为value
        # redis_conn = get_redis_connection('verify_codes')

        # redis_conn.set('<key>','<value>','<expires>')
        # redis_conn.setex('<key>','<expires>','<value>')
        # redis_conn.setex('sms_%s' % mobile,constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex('send_flag_%s' % mobile,constants.SEND_SMS_CODE_INTERVAL,1)

        # 创建redis管道对象
        pl = redis_conn.pipeline()

        # 向redis管道中添加命令
        pl.setex('sms_%s' % mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        pl.setex('send_flag_%s' % mobile,constants.SEND_SMS_CODE_INTERVAL, 1)

        # 一次性执行管道中的所有命令
        pl.execute()
        # 3.使用云通讯给mobile发送短信
        expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        # 创建一个进程调用发送短信的函数
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile,sms_code,expires)
        # 4.返回应答，短信发送成功
        return Response({'message':'OK'})
