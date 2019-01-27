from django.test import TestCase
from urllib.parse import urlencode
from urllib.parse import parse_qs
from urllib.request import urlopen
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from itsdangerous import BadData
# itsdangerous:进行数据的签名加密和解密
# 安装：pip install itsdangerous
# Create your tests here.

if __name__ == '__main__':
    req_data = 'eyJleHAiOjE1NDg1OTgxMTcsImlhdCI6MTU0ODU5NDUxNywiYWxnIjoiSFMyNTYifQ.eyJvcGVuaWQiOiJLREtLU0RKSkRKVVExMjgzaUtETExEIn0.F8gpRRj9P_WxPbLjruKwC-x1EuV1vDKs_m8iSuAWfbM'

    # 解密
    serializer = TJWSSerializer(secret_key='2123456abc')
    try:

        res_dict = serializer.loads(req_data)
    except BadData:
        print("解密失败")
    else:

    # res = res_dict.get('openid',"")
        print(res_dict)
# if __name__ == '__main__':
#     my_dict = {
#         'openid':'KDKKSDJJDJUQ1283iKDLLD'
#     }
#     # 签名加密
#     # TJWSSerializer(secret_key='秘钥',expires_in='解密有效时间:s‘)
#     serializer = TJWSSerializer(secret_key='123456abc',expires_in=3600)
#     res = serializer.dumps(my_dict) # bytes
#     # bytes -- > str
#     res = res.decode()
#     print(res)

# if __name__ == '__main__':
#     # urlopen(url): 发起http请求
#     req_url = 'http://api.meiduo.site:8000/mobiles/13155667788/count/'
#     # 发起http网络请求
#     response = urlopen(req_url)
#
#     # 获取响应数据
#     res_data = response.read() # 响应数据为bytes
#     # bytes -- > str
#     res_data = res_data.decode()
#     # {"count":0,"mobile":"13155667788"}
#     print(res_data)

# if __name__ == '__main__':
#     # parse_qs(qs): 将查询字符串转换为字典
#     qs = 'c=3&b=2&a=1'
#     # {'a': ['1'], 'c': ['3'], 'b': ['2']}
#     res = parse_qs(qs)
#     print(res) # 注意：转换为字典，key对应的value类型是list
# if __name__ == '__main__':
#     # urlencode(dict) :将字典转换为查询字符串
#     data = {
#         'a':1,
#         'b':2,
#         'c':3
#     }
#     res = urlencode(data)
#     print(res)
