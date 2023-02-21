#!/usr/bin/env python
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

import sys

from kubernetes import client, config

from bucket import BucketConfig
from contants import BACKUP_REPO_SECRET, BACKUP_REPO_SECRET_KEY, MINIO_CREDENTIALS_SECRET, \
    MINIO_CREDENTIALS_SECRET_ACCESS_KEY, MINIO_CREDENTIALS_SECRET_SECRET_KEY, \
    LOCAL, S3

sys.path.append("test/utils")
import util


class RestoreConfig(object):
    def __init__(self, backup, storage_class, backend_type):
        self.backup = backup
        self.storage_class = storage_class
        self.backend_type = backend_type


class Restore(object):
    def __init__(self, name, namespace):
        config.load_kube_config()
        self.api = client.CustomObjectsApi()
        self.name = name
        self.namespace = namespace
        self.created = False

    def create(self,
               chain,
               node,
               deploy_method="cloud-config",
               restore_config: RestoreConfig = None,
               bucket_config: BucketConfig = None):
        if restore_config.backend_type == LOCAL:
            self.create_from_local(chain, node, restore_config.backup, deploy_method, restore_config.storage_class)
        elif restore_config.backend_type == S3:
            self.create_form_s3(chain, node, restore_config.backup, deploy_method,
                                endpoint=bucket_config.endpoint,
                                bucket=bucket_config.name)
        else:
            raise Exception("mismatch restore backend type")

    def create_from_local(self,
                          chain,
                          node,
                          backup,
                          deploy_method="cloud-config",
                          storage_class="nas-client-provisioner"):
        resource_body = {
            "apiVersion": "rivtower.com/v1cita",
            "kind": "Restore",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "deployMethod": deploy_method,
                "backup": backup,
                "restoreMethod": {
                    "folder": {
                        "claimName": "datadir-{}-0".format(node)
                    }
                },
                "backend": {
                    "repoPasswordSecretRef": {
                        "name": BACKUP_REPO_SECRET,
                        "key": BACKUP_REPO_SECRET_KEY,
                    },
                    "local": {
                        "mountPath": "/hello",
                        "storageClass": storage_class,
                    }
                }
            },
        }
        # create a cluster scoped resource
        self.api.create_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            namespace=self.namespace,
            plural="restores",
            body=resource_body,
        )
        self.created = True

    def create_form_s3(self,
                       chain,
                       node,
                       backup,
                       deploy_method="cloud-config",
                       endpoint="minio.zhujq:9000",
                       bucket="k8up-full"):
        resource_body = {
            "apiVersion": "rivtower.com/v1cita",
            "kind": "Restore",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "deployMethod": deploy_method,
                "backup": backup,
                "restoreMethod": {
                    "folder": {
                        "claimName": "datadir-{}-0".format(node)
                    }
                },
                "backend": {
                    "repoPasswordSecretRef": {
                        "name": BACKUP_REPO_SECRET,
                        "key": BACKUP_REPO_SECRET_KEY,
                    },
                    "s3": {
                        "endpoint": "http://" + endpoint,
                        "bucket": bucket,
                        "accessKeyIDSecretRef": {
                            "name": MINIO_CREDENTIALS_SECRET,
                            "key": MINIO_CREDENTIALS_SECRET_ACCESS_KEY
                        },
                        "secretAccessKeySecretRef": {
                            "name": MINIO_CREDENTIALS_SECRET,
                            "key": MINIO_CREDENTIALS_SECRET_SECRET_KEY,
                        },
                    }
                }
            },
        }
        # create a cluster scoped resource
        self.api.create_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            namespace=self.namespace,
            plural="restores",
            body=resource_body,
        )
        self.created = True

    def wait_job_complete(self):
        return util.wait_new_job_complete("restores", self.name, self.namespace)

    def delete(self):
        self.api.delete_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            name=self.name,
            namespace=self.namespace,
            plural="restores",
            body=client.V1DeleteOptions(),
        )

    def status(self):
        pass
