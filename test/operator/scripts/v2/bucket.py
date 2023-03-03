#
# Copyright Rivtower Technologies LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from minio import Minio


class Bucket(object):
    client = None

    def __new__(cls, *args, **kwargs):
        if not cls.client:
            cls.client = object.__new__(cls)
        return cls.client

    def __init__(self, service, access_key, secret_key, secure=False):
        self.service = service
        self.client = Minio(service, access_key=access_key, secret_key=secret_key, secure=secure)

    def exists_bucket(self, bucket_name):
        """
        判断桶是否存在
        :param bucket_name: 桶名称
        :return:
        """
        return self.client.bucket_exists(bucket_name=bucket_name)

    def remove_bucket(self, bucket_name):
        """
        删除桶
        :param bucket_name:
        :return:
        """
        try:
            objects = self.client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                self.client.remove_object(bucket_name, obj.object_name)
            # remove bucket
            self.client.remove_bucket(bucket_name=bucket_name)
        except Exception as e:
            raise Exception(e)


class BucketConfig(object):
    def __init__(self, name, endpoint, access_key, secret_key):
        self.name = name
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key


if __name__ == '__main__':
    # b = Bucket(service="192.168.10.120:30289", access_key="minio", secret_key="minio123")
    pass