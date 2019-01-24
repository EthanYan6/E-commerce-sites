
def jwt_response_payload_handler(token,user=None,request=None):
    """
    自定义jwt扩展登录视图的响应数据函数

    """
    return {
        'user_id':user.id,
        'username':user.username,
        'token':token
    }
