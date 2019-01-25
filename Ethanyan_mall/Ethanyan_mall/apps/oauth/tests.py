from django.test import TestCase
from urllib.parse import urlencode
from urllib.parse import parse_qs
from urllib.request import urlopen
# Create your tests here.

if __name__ == '__main__':
    # urlopen(url): 发起http请求
    req_url = 'http://api.meiduo.site:8000/mobiles/13155667788/count/'
    # 发起http网络请求
    response = urlopen(req_url)

    # 获取响应数据
    res_data = response.read() # 响应数据为bytes
    # bytes -- > str
    res_data = res_data.decode()
    # {"count":0,"mobile":"13155667788"}
    print(res_data)

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
