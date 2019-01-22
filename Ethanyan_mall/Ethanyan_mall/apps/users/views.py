from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.

# # 测试session数据库配置
# # /set_session、
# def set_session(request):
#     #设置session
#     request.session['name'] = 'Ethanyan'
#     request.session['work'] = 'Coder'
#     return HttpResponse('set session...')
#
# # /get_session
# def get_session(request):
#     # 获取session信息
#     name = request.session.get('name')
#     work = request.session.get('work')
#     return HttpResponse('name:%s -- work:%s'%(name,work))
#
# # 自定义异常处理测试
# # GET /goods/
# class GoodsView(APIView):
#     def get(self,request):
#         # 抛出数据库异常
#         raise DatabaseError
#         return Response({'message':'OK'})