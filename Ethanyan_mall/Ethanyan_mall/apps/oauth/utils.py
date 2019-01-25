import json
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from itsdangerous import BadData

from .exceptions import QQAPIError

from django.conf import settings


class OAuthQQ(object):
    # 对openid进行加解密的安全密钥
    SECRET_KEY = settings.SECRET_KEY
    # 对openid加密之后生成的access_token的有效时间
    EXPIRES_IN = 10 * 60

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        # QQ网站应用客户端id
        self.client_id = client_id or settings.QQ_CLIENT_ID
        # QQ网站应用客户端安全密钥
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        # 网站回调url网址
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE

    def get_login_url(self):
        """
        获取QQ的登录网址:
        """
        # 组织参数
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info'
        }

        # 拼接url地址
        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)

        return url

    def get_access_token(self, code):
        """
        获取access_token:
        code: QQ提供的code
        """
        # 组织参数
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
        }

        # 拼接url地址
        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)
        try:
            # 访问获取accesss_token
            response = urlopen(url)
        except Exception as e:
            raise QQAPIError

        # 返回数据格式如下:
        # access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE14
        # 获取响应数据并解码
        res_data = response.read().decode()
        # 转化成字典
        res_dict = parse_qs(res_data)

        # 尝试从字典中获取access_token
        access_token = res_dict.get('access_token')

        if not access_token:
            # 获取access_token失败
            raise QQAPIError

        # 返回access_token
        return access_token[0]

    def get_openid(self, access_token):
        """
        获取QQ授权用户的openid:
        access_token: QQ返回的access_token
        """
        # 拼接url地址
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        try:
            # 访问获取QQ授权用户的openid
            response = urlopen(url)
        except Exception as e:
            raise QQAPIError

        # 返回数据格式如下:
        # callback( {"client_id": "YOUR_APPID", "openid": "YOUR_OPENID"} );\n
        res_data = response.read().decode()
        try:
            res_dict = json.loads(res_data[10:-4])
        except Exception as e:
            raise QQAPIError

        # 获取openid
        openid = res_dict.get('openid')
        return openid

    @classmethod
    def generate_save_user_token(cls, openid, secret_key=None, expires=None):
        """
        对openid进行加密:
        openid: QQ授权用户的openid
        secret_key: 密钥
        expires: token有效时间
        """
        if secret_key is None:
            secret_key = cls.SECRET_KEY

        if expires is None:
            expires = cls.EXPIRES_IN

        serializer = TJWSSerializer(secret_key, expires)

        token = serializer.dumps({'openid': openid})
        return token.decode()

    @classmethod
    def check_save_user_token(cls, token, secret_key=None, expires=None):
        """
        对token进行校验:
        token: 对openid加密之后生成的token
        secret_key: 密钥
        expires: token有效时间
        """
        if secret_key is None:
            secret_key = cls.SECRET_KEY

        if expires is None:
            expires = cls.EXPIRES_IN

        serializer = TJWSSerializer(secret_key, expires)

        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            return data.get('openid')
