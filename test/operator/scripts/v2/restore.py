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

import kubernetes.client.exceptions
from kubernetes import client, config

from bucket import BucketConfig
from contants import BACKUP_REPO_SECRET, BACKUP_REPO_SECRET_KEY, MINIO_CREDENTIALS_SECRET, \
    MINIO_CREDENTIALS_SECRET_ACCESS_KEY, MINIO_CREDENTIALS_SECRET_SECRET_KEY, \
    LOCAL, S3, LOCAL_WITH_EXIST_PVC

sys.path.append("test/utils")
import util
from logger import logger


class RestoreConfig(object):
    def __init__(self,
                 backup,
                 storage_class,
                 backend_type,
                 pvc="integration-test-pvc",
                 mount_path="/bk/node_backup"):
        self.backup = backup
        self.storage_class = storage_class
        self.backend_type = backend_type
        self.pvc = pvc
        self.mount_path = mount_path


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
        elif restore_config.backend_type == LOCAL_WITH_EXIST_PVC:
            self.create_from_local_with_exist_pvc(chain,
                                                  node,
                                                  restore_config.backup,
                                                  deploy_method,
                                                  pvc=restore_config.pvc,
                                                  mount_path=restore_config.mount_path)
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
                          storage_class="nas-client-provisioner",
                          action="StopAndStart"):
        resource_body = {
            "apiVersion": "rivtower.com/v1cita",
            "kind": "Restore",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "deployMethod": deploy_method,
                "action": action,
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

    def create_from_local_with_exist_pvc(self,
                                         chain,
                                         node,
                                         backup,
                                         deploy_method="cloud-config",
                                         pvc="nas-client-provisioner",
                                         mount_path="/bk/node-backup",
                                         action="StopAndStart"):
        resource_body = {
            "apiVersion": "rivtower.com/v1cita",
            "kind": "Restore",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "deployMethod": deploy_method,
                "action": action,
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
                        "mountPath": mount_path,
                        "pvc": pvc,
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
                       bucket="k8up-full",
                       action="StopAndStart"):
        resource_body = {
            "apiVersion": "rivtower.com/v1cita",
            "kind": "Restore",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "deployMethod": deploy_method,
                "action": action,
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

    def clear(self):
        try:
            _ = self.api.get_namespaced_custom_object(
                group="rivtower.com",
                version="v1cita",
                name=self.name,
                namespace=self.namespace,
                plural="restores",
            )
            self.delete()
            logger.debug("delete old resource {}/{} successful".format(self.namespace, self.name))
        except kubernetes.client.exceptions.ApiException:
            logger.debug("the resource {}/{} have been deleted, pass...".format(self.namespace, self.name))

    def status(self) -> str:
        resource = self.api.get_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            name=self.name,
            namespace=self.namespace,
            plural="restores",
        )
        if not resource.get('status'):
            return "No Status"
        for condition in resource.get('status').get('conditions'):
            if condition.get('type') == 'Completed':
                return condition.get('reason')
