# 封装发送邮件的任务函数
from celery_tasks.main import celery_app
from django.conf import settings
from django.core.mail import send_mail
@celery_app.task(name='send_verify_email')
def send_verify_email(to_email,verfy_url):
    subject = "闫氏商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>你咋这么有眼光呢？欢迎使用我们闫氏商城。</p>' \
                   '<p>您的邮箱为：%s。请点击此链接（就是这个有蓝色下划线的东西）激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' %(to_email,verfy_url,verfy_url)
    send_mail(subject,"",settings.EMAIL_FROM,[to_email],html_message=html_message)

