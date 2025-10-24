"""
@File    :qiniu_cloud.py
@Editor  : 百年
@Date    :2025/10/3 15:22 
"""
# tips:封装七牛云的对象存储，用来存储上传的照片

# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_file_v2, etag, put_data  # putdata是七牛云封装的上传二进制的方法
import qiniu.config
import time
import random
from qiniu import BucketManager


def upload_qiniu(filestorage, pic_key, pic_suffix):
    # 需要填写你的 Access Key 和 Secret Key
    access_key = '8Hxcq9GWT0CWCfyPVaVkGkwJTagxaVu8PCQzOuB8'
    secret_key = 'jiz7Pyuo5Th5f0aPnb5bwO9VHOUYCkbBkkewy8eY'

    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    # bucket_name = 'viminblog' #important:私有云访问也可以!!!1
    bucket_name = 'vimin'  # 这边换成共有云，这样便可以进行查询mysql并将其展示出来了

    # 上传后保存的文件名
    # key = 'my-python-logo.png'
    # tips:设置文件名的时候一定要考虑的问题,那就是如果多个用户上传同名文件是危险的!!!
    key = pic_key + str(int(time.time()) + random.randint(0, 9)) + '.' + pic_suffix

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    # 要上传文件的本地路径
    # localfile = ''

    # ret, info = put_file_v2(token, key, localfile, version='v2')
    # ret, info = put_file_v2(token, key, version='v2')
    ret, info = put_data(token, key, filestorage.read())
    print(info)

    return info, ret
    # assert ret['key'] == key
    # assert ret['hash'] == etag(localfile)


def del_qiniu(picname):
    # 需要填写你的 Access Key 和 Secret Key
    access_key = '8Hxcq9GWT0CWCfyPVaVkGkwJTagxaVu8PCQzOuB8'
    secret_key = 'jiz7Pyuo5Th5f0aPnb5bwO9VHOUYCkbBkkewy8eY'
    # 初始化Auth状态
    q = Auth(access_key, secret_key)
    # 初始化BucketManager
    bucket = BucketManager(q)
    # 你要测试的空间， 并且这个key在你空间中存在
    bucket_name = 'vimin'
    key =picname
    # 删除bucket_name 中的文件 key
    ret, info = bucket.delete(bucket_name, key)
    print(info)
    # assert ret == {}
    return info.status_code
