from django.core.files.storage import Storage
from django.conf import settings
from django.utils.deconstruct import deconstructible

from fdfs_client.client import Fdfs_client


@deconstructible
class FDFSStorage(Storage):
    """FDFS文件存储类"""
    def __init__(self, client_conf=None, base_url=None):
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF

        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_NGINX_URL

        self.base_url = base_url

    def _save(self, name, content):
        """
        name: 上传文件的名称 1.jpg
        content: 包含上传文件内容的File对象，可以通过content.read()获取上传文件内容
        """
        # 将文件上传的FDFS文件存储系统
        client = Fdfs_client(self.client_conf)

        res = client.upload_by_buffer(content.read())

        if res.get('Status') != 'Upload successed.':
            raise Exception('上传文件到FDFS系统失败')

        # 获取文件ID
        file_id = res.get('Remote file_id')

        return file_id

    def exists(self, name):
        """
        Django系统调用文件存储类中的_save保存文件之前，会先调用exists这个方法
        来判断文件名是否跟文件系统中原有的文件发生了冲突
        name: 1.jpg
        """
        return False

    def url(self, name):
        """
        获取可访问的文件完整url路径
        name：表中存储的image字段的内容
        """
        return self.base_url + name



