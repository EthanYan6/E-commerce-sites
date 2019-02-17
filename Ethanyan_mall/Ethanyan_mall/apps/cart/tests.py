import base64

from django.test import TestCase
import pickle
# Create your tests here.


# pickle.dumps(dict|对象):将传入的数据转换为bytes字节流
# pickle.loads(bytes字节流):将bytes字节流转换为dict或者对象
if __name__ == '__main__':
    req_data = 'gAN9cQAoSwF9cQEoWAUAAABjb3VudHECSwJYCAAAAHNlbGVjdGVkcQOIdUsDfXEEKGgCSwFoA4l1dS4='
    # res = req_data.encode()
    # print(res)
    # res = base64.b64decode(res)
    # print(res)
    # res = pickle.loads(res)
    # print(res)
    print(pickle.loads(base64.b64decode(req_data)))

# if __name__ == '__main__':
#     cart_dict ={
#         1:{
#             'count':2,
#             'selected':True
#         },
#         3:{
#             'count':1,
#             'selected':False
#         }
#     }
#
#     # pickle.dumps
#     res = pickle.dumps(cart_dict)
#     print(res)
#
#
#
#     #base64.b64encode
#     str = base64.b64encode(res)
#     print(str)
#     #
#     # # bytes->str
#     res = str.decode()
#     print(res)
    # # base64.b64encode
    # res = base64.b64encode(res)
    # print(res)

    # req_data = b'\x80\x03}q\x00(K\x01}q\x01(X\x05\x00\x00\x00countq\x02K\x02X\x08\x00\x00\x00selectedq\x03\x88uK\x03}q\x04(h\x02K\x01h\x03\x89uu.'
    # # pickle.loads
    # # res = pickle.loads(req_data)
    # # print(res)
    # res = base64.b64decode(req_data)
    # print(res)


