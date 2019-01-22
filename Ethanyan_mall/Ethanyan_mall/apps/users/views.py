from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

# 测试session数据库配置
# /set_session、
def set_session(request):
    #设置session
    request.session['name'] = 'Ethanyan'
    request.session['work'] = 'Coder'
    return HttpResponse('set session...')

# /get_session
def get_session(request):
    # 获取session信息
    name = request.session.get('name')
    work = request.session.get('work')
    return HttpResponse('name:%s -- work:%s'%(name,work))

