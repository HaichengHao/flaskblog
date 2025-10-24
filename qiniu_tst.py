# from qiniu import Auth
# from qiniu import BucketManager
#
# access_key = '8Hxcq9GWT0CWCfyPVaVkGkwJTagxaVu8PCQzOuB8'
# secret_key = 'jiz7Pyuo5Th5f0aPnb5bwO9VHOUYCkbBkkewy8eY'
# bucket_name = 'vimin'
# q = Auth(access_key, secret_key)
# bucket = BucketManager(q)
# # 要拉取的文件名
# key = '2023-04-07_2221371759716625.png'
# ret, info = bucket.prefetch(bucket_name, key)
# print(info)


# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth
from qiniu import BucketManager
access_key = '8Hxcq9GWT0CWCfyPVaVkGkwJTagxaVu8PCQzOuB8'
secret_key = 'jiz7Pyuo5Th5f0aPnb5bwO9VHOUYCkbBkkewy8eY'
bucket_name = 'vimin'
q = Auth(access_key, secret_key)
bucket = BucketManager(q)
# 要拉取的文件名
key = '2023-08-11_1006121759642910.png'
ret, info = bucket.prefetch(bucket_name, key)
print(info)