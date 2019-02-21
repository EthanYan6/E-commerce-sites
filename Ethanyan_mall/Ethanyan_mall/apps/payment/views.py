import os

from alipay import AliPay
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from orders.models import OrderInfo




# Create your views here.



# GET /orders/(?P<order_id>\d+)/payment/
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,order_id):
        """
        获取支付宝支付网址
        1.获取order_id并校验订单是否有效
        2.组织支付宝支付网址和参数
        3.返回支付宝支付网址
        """
        user = request.user

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=OrderInfo.PAY_METHODS_ENUM['ALIPAY'],
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                                          )
        except OrderInfo.DoesNotExist:
            return Response({'message': '无效的订单id'}, status=status.HTTP_400_BAD_REQUEST)

        # 初始化
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,  # 开发应用appid
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/payment/keys/app_private_key.pem'),
            # 网站的私钥文件路径
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/payment/keys/alipay_public_key.pem'),
            # 支付宝公钥文件路径
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        # 组织支付参数
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        total_pay = order.total_amount  # Decimal
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单id
            total_amount=str(total_pay),
            subject='闫氏商城%s' % order_id,  # 订单标题
            return_url="http://www.meiduo.site:8080/pay_success.html",  # 回调地址
        )

        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return Response({'alipay_url': alipay_url})
