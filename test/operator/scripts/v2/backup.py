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

import base64
import os
import sys
import time

import kubernetes.client.exceptions
from kubernetes import client, config

from bucket import Bucket, BucketConfig
from contants import FULL_BACKUP, STATE_BACKUP, LOCAL, LOCAL_WITH_EXIST_PVC, S3, BACKUP_REPO_SECRET, \
    BACKUP_REPO_SECRET_KEY, \
    MINIO_CREDENTIALS_SECRET, \
    MINIO_CREDENTIALS_SECRET_ACCESS_KEY, MINIO_CREDENTIALS_SECRET_SECRET_KEY
from pvc import prepare_pvc
from restore import Restore, RestoreConfig

sys.path.append("test/utils")
import util
from logger import logger


class BackupConfig(object):
    def __init__(self,
                 backup_type,
                 backend_type,
                 block_height=10,
                 storage_class="nas-client-provisioner",
                 pvc="integration-test-pvc",
                 mount_path="/bk/node_backup"):
        self.backup_type = backup_type
        self.backend_type = backend_type
        self.block_height = block_height
        self.storage_class = storage_class
        self.pvc = pvc
        self.mount_path = mount_path


class Backup(object):

    def __init__(self, name, namespace):
        config.load_kube_config()
        self.custom_api = client.CustomObjectsApi()
        self.core_api = client.CoreV1Api()
        self.name = name
        self.namespace = namespace
        # crate or not
        self.created = False

    def _prepare_backup_repo(self, namespace, name="backup-repo", password="p@ssw0rd"):
        """
        prepare backup repo secret
        :param namespace:
        :param name:
        :return:
        """
        try:
            self.core_api.read_namespaced_secret(name, namespace)
            logger.debug("the backup repo secret already exist")
        except kubernetes.client.exceptions.ApiException:
            logger.debug("create backup repo secret {}/{} ...".format(namespace, name))
            secret = client.V1Secret()
            secret.api_version = 'v1'
            data = {'password': str(base64.b64encode(password.encode(encoding="utf-8")), "utf-8")}
            secret.data = data
            secret.kind = 'Secret'
            secret.metadata = {"name": name}
            secret.type = 'Opaque'
            self.core_api.create_namespaced_secret(namespace, secret, pretty="true")
            logger.debug("create backup repo secret {}/{} successful".format(namespace, name))

    def _prepare_minio_credentials(self, namespace,
                                   name=MINIO_CREDENTIALS_SECRET,
                                   username="minio",
                                   password="minio123"):
        """
        prepare minio credentials secret
        :param namespace:
        :param name:
        :return:
        """
        try:
            self.core_api.read_namespaced_secret(name, namespace)
            logger.debug("the minio credentials secret already exist")
        except kubernetes.client.exceptions.ApiException:
            logger.debug("create minio credentials secret {}/{} ...".format(namespace, name))
            secret = client.V1Secret()
            secret.api_version = 'v1'
            data = {
                'username': str(base64.b64encode(username.encode(encoding="utf-8")), "utf-8"),
                'password': str(base64.b64encode(password.encode(encoding="utf-8")), "utf-8"),
            }
            secret.data = data
            secret.kind = 'Secret'
            secret.metadata = {"name": name}
            secret.type = 'Opaque'
            self.core_api.create_namespaced_secret(namespace, secret, pretty="true")
            logger.debug("create minio credentials secret {}/{} successful".format(namespace, name))

    def _prepare(self, bucket_cfg: BucketConfig = None):
        self._prepare_backup_repo(self.namespace)
        if bucket_cfg is not None:
            self._prepare_minio_credentials(self.namespace,
                                            name=MINIO_CREDENTIALS_SECRET,
                                            username=bucket_cfg.access_key,
                                            password=bucket_cfg.secret_key)

    def create(self,
               chain,
               node,
               deploy_method="cloud-config",
               backup_cfg: BackupConfig = None,
               bucket_cfg: BucketConfig = None):
        # check secret
        self._prepare(bucket_cfg)

        if backup_cfg.backend_type == LOCAL:
            self._local_backup(chain,
                               node,
                               backup_type=backup_cfg.backup_type,
                               deploy_method=deploy_method,
                               storage_class=backup_cfg.storage_class,
                               block_height=backup_cfg.block_height)
        elif backup_cfg.backend_type == LOCAL_WITH_EXIST_PVC:
            self._local_backup_with_exist_pvc(chain,
                                              node,
                                              backup_type=backup_cfg.backup_type,
                                              deploy_method=deploy_method,
                                              pvc=backup_cfg.pvc,
                                              mount_path=backup_cfg.mount_path,
                                              block_height=backup_cfg.block_height)
        elif backup_cfg.backend_type == S3:
            minio_obj = Bucket(service=bucket_cfg.endpoint,
                               access_key=bucket_cfg.access_key,
                               secret_key=bucket_cfg.secret_key)
            # remove if onj exist
            if minio_obj.exists_bucket(bucket_cfg.name):
                logger.debug("bucket {} exist, remove it...".format(bucket_cfg.name))
                minio_obj.remove_bucket(bucket_cfg.name)
            self._s3_backup(chain,
                            node,
                            backup_type=backup_cfg.backup_type,
                            deploy_method=deploy_method,
                            endpoint=bucket_cfg.endpoint,
                            bucket=bucket_cfg.name,
                            block_height=backup_cfg.block_height)
        else:
            raise Exception("mismatched backend type")

    def _local_backup(self,
                      chain,
                      node,
                      backup_type=FULL_BACKUP,
                      deploy_method="cloud-config",
                      storage_class="nas-client-provisioner",
                      block_height=10):
        """
        创建本地备份
        :param chain:
        :param node:
        :param backup_type:
        :param deploy_method:
        :param storage_class:
        :param block_height: 块高，当backup_type为状态备份时，需要指定该值
        :return:
        """
        # resource_body = None
        if backup_type == FULL_BACKUP:
            resource_body = {
                "apiVersion": "rivtower.com/v1cita",
                "kind": "Backup",
                "metadata": {"name": self.name},
                "spec": {
                    "chain": chain,
                    "node": node,
                    "deployMethod": deploy_method,
                    "dataType": {
                        "full": {
                            "includePaths": ["data", "chain_data"]
                        }
                    },
                    "failedJobsHistoryLimit": 2,
                    "successfulJobsHistoryLimit": 2,
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
        elif backup_type == STATE_BACKUP:
            resource_body = {
                "apiVersion": "rivtower.com/v1cita",
                "kind": "Backup",
                "metadata": {"name": self.name},
                "spec": {
                    "chain": chain,
                    "node": node,
                    "deployMethod": deploy_method,
                    "dataType": {
                        "state": {
                            "blockHeight": block_height
                        }
                    },
                    "failedJobsHistoryLimit": 2,
                    "successfulJobsHistoryLimit": 2,
                    "backend": {
                        "repoPasswordSecretRef": {
                            "name": BACKUP_REPO_SECRET,
                            "key": BACKUP_REPO_SECRET_KEY,
                        },
                        "local": {
                            "mountPath": "/hello",
                            "storageClass": storage_class,
                            "size": "10Gi"
                        }
                    }
                },
            }
        else:
            raise Exception("mismatched backup type")
        # create a cluster scoped resource
        self.custom_api.create_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            namespace=self.namespace,
            plural="backups",
            body=resource_body,
        )
        self.created = True

    def _local_backup_with_exist_pvc(self,
                                     chain,
                                     node,
                                     backup_type=FULL_BACKUP,
                                     deploy_method="cloud-config",
                                     pvc="nas-client-provisioner",
                                     mount_path="/bk/node-backup",
                                     block_height=10):
        """
        创建本地备份(用户提供pvc)
        :param chain:
        :param node:
        :param backup_type:
        :param deploy_method:
        :param pvc: pvc name
        :param mount_path: 挂载点
        :param block_height: 块高,状态备份时使用
        :return:
        """
        if backup_type == FULL_BACKUP:
            resource_body = {
                "apiVersion": "rivtower.com/v1cita",
                "kind": "Backup",
                "metadata": {"name": self.name},
                "spec": {
                    "chain": chain,
                    "node": node,
                    "deployMethod": deploy_method,
                    "dataType": {
                        "full": {
                            "includePaths": ["data", "chain_data"]
                        }
                    },
                    "failedJobsHistoryLimit": 2,
                    "successfulJobsHistoryLimit": 2,
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
        elif backup_type == STATE_BACKUP:
            resource_body = {
                "apiVersion": "rivtower.com/v1cita",
                "kind": "Backup",
                "metadata": {"name": self.name},
                "spec": {
                    "chain": chain,
                    "node": node,
                    "deployMethod": deploy_method,
                    "dataType": {
                        "state": {
                            "blockHeight": block_height
                        }
                    },
                    "failedJobsHistoryLimit": 2,
                    "successfulJobsHistoryLimit": 2,
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
        else:
            raise Exception("mismatched backup type")
        # create a cluster scoped resource
        self.custom_api.create_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            namespace=self.namespace,
            plural="backups",
            body=resource_body,
        )
        self.created = True

    def _s3_backup(self,
                   chain,
                   node,
                   backup_type=FULL_BACKUP,
                   deploy_method="cloud-config",
                   endpoint="minio.zhujq:9000",
                   bucket="k8up-full",
                   block_height=10):
        if backup_type == FULL_BACKUP:
            resource_body = {
                "apiVersion": "rivtower.com/v1cita",
                "kind": "Backup",
                "metadata": {"name": self.name},
                "spec": {
                    "chain": chain,
                    "node": node,
                    "deployMethod": deploy_method,
                    "dataType": {
                        "full": {
                            "includePaths": ["data", "chain_data"]
                        }
                    },
                    "failedJobsHistoryLimit": 3,
                    "successfulJobsHistoryLimit": 3,
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
        elif backup_type == STATE_BACKUP:
            resource_body = {
                "apiVersion": "rivtower.com/v1cita",
                "kind": "Backup",
                "metadata": {"name": self.name},
                "spec": {
                    "chain": chain,
                    "node": node,
                    "deployMethod": deploy_method,
                    "dataType": {
                        "state": {
                            "blockHeight": block_height
                        }
                    },
                    "failedJobsHistoryLimit": 3,
                    "successfulJobsHistoryLimit": 3,
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
        else:
            raise Exception("mismatched backup type")

        # create a cluster scoped resource
        self.custom_api.create_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            namespace=self.namespace,
            plural="backups",
            body=resource_body,
        )
        self.created = True

    def wait_job_complete(self):
        return util.wait_new_job_complete("backups", self.name, self.namespace)

    def delete(self):
        self.custom_api.delete_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            name=self.name,
            namespace=self.namespace,
            plural="backups",
            body=client.V1DeleteOptions(),
        )

    def clear(self):
        try:
            _ = self.custom_api.get_namespaced_custom_object(
                group="rivtower.com",
                version="v1cita",
                name=self.name,
                namespace=self.namespace,
                plural="backups",
            )
            self.delete()
            logger.debug("delete old resource {}/{} successful".format(self.namespace, self.name))
        except kubernetes.client.exceptions.ApiException:
            logger.debug("the resource {}/{} have been deleted, pass...".format(self.namespace, self.name))

    def status(self) -> str:
        resource = self.custom_api.get_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            name=self.name,
            namespace=self.namespace,
            plural="backups",
        )
        if not resource.get('status'):
            return "No Status"
        for condition in resource.get('status').get('conditions'):
            if condition.get('type') == 'Completed':
                return condition.get('reason')


def create_backup_and_restore(namespace,
                              backup_name,
                              restore_name,
                              backup_cfg: BackupConfig = None,
                              bucket_cfg: BucketConfig = None,
                              restore_cfg: RestoreConfig = None):
    backup = Backup(namespace=namespace, name=backup_name)
    backup.clear()
    restore = Restore(namespace=namespace, name=restore_name)
    restore.clear()
    try:
        logger.debug("========================>")
        logger.debug("exec backup and restore, backup type: {}, backend type: {}".format(backup_cfg.backup_type,
                     backup_cfg.backend_type))
        logger.debug("========================>")

        # get block number when backup
        bn_with_backup = util.get_block_number()
        logger.info("the block number before backup is: {}".format(bn_with_backup))
        # create backup job
        logger.info("create backup job...")
        backup.create(chain=os.getenv("CHAIN_NAME"),
                      node="{}-node0".format(os.getenv("CHAIN_NAME")),
                      backup_cfg=backup_cfg,
                      bucket_cfg=bucket_cfg)
        status = backup.wait_job_complete()
        if status == "Failed":
            raise Exception("backup exec failed")
        logger.info("the backup job has been completed")
        # check work well
        util.check_block_increase()
        logger.info(
            "create backup for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))

        # when difference > 200
        while True:
            now_bn = util.get_block_number()
            if now_bn - bn_with_backup > 200:
                break
            logger.info(
                "waiting and exceeds the 200 block height at the time of backup, current block number: {}...".format(
                    now_bn))
            time.sleep(2)
        # latest block number
        bn_with_latest = util.get_block_number()
        logger.info("the latest block number after waiting is: {}".format(bn_with_latest))

        # create restore job
        logger.info("create restore job for backup...")
        restore.create(chain=os.getenv("CHAIN_NAME"),
                       node="{}-node0".format(os.getenv("CHAIN_NAME")),
                       restore_config=restore_cfg,
                       bucket_config=bucket_cfg)
        status = restore.wait_job_complete()
        if status == "Failed":
            raise Exception("restore for backup exec failed")
        logger.info("the restore job for backup has been completed")

        util.check_node_running(name="{}-node0".format(os.getenv("CHAIN_NAME")), namespace=os.getenv("NAMESPACE"))

        node_syncing_status = util.get_node_syncing_status(retry_times=30, retry_wait=3)
        logger.debug("node status after backup restore is: {}".format(node_syncing_status))

        bn_with_recover = node_syncing_status["self_status"]["height"]
        logger.info("the block number after backup restore is: {}".format(bn_with_recover))
        if bn_with_recover > bn_with_latest:
            raise Exception("restore not excepted block number: bn_with_recover is {}, bn_with_latest is {}".
                            format(bn_with_recover, bn_with_latest))
        logger.info(
            "create restore for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))

        # wait for the consensus block to determine whether the node is ok
        util.wait_block_number_exceed_specified_height(specified_height=bn_with_latest, retry_times=200, retry_wait=3)
    except Exception as s:
        logger.exception(s)
        exit(10)
    finally:
        logger.debug("<========================")
        logger.debug("exec backup and restore, backup type: {}, backend type: {}".format(backup_cfg.backup_type,
                     backup_cfg.backend_type))
        logger.debug("<========================")
        if restore.created and restore.status() == "Succeeded":
            restore.delete()
        if backup.created and backup.status() == "Succeeded":
            backup.delete()


def execute_job(backup_type: str = FULL_BACKUP, backend_type: str = LOCAL):
    backup_name = "backup-{}".format(os.getenv("CHAIN_TYPE"))
    backup_cfg = BackupConfig(backup_type=backup_type,
                              backend_type=backend_type,
                              # 快照至5#
                              block_height=5,
                              storage_class="nas-client-provisioner",
                              pvc="integration-test-pvc",
                              mount_path="/bk/node_backup")
    bucket_cfg = BucketConfig(name="integration-bucket",
                              endpoint="minio.zhujq:9000",
                              access_key="minio",
                              secret_key="minio123")
    restore_cfg = RestoreConfig(backup=backup_name,
                                storage_class="nas-client-provisioner",
                                backend_type=backend_type,
                                pvc="integration-test-pvc",
                                mount_path="/bk/node_backup")
    create_backup_and_restore(namespace=os.getenv("NAMESPACE"),
                              backup_name=backup_name,
                              restore_name="restore-for-backup-{}".format(os.getenv("CHAIN_TYPE")),
                              backup_cfg=backup_cfg,
                              restore_cfg=restore_cfg,
                              bucket_cfg=bucket_cfg
                              )


if __name__ == '__main__':
    prepare_pvc()
    execute_job(backup_type=FULL_BACKUP, backend_type=LOCAL)
    execute_job(backup_type=FULL_BACKUP, backend_type=LOCAL_WITH_EXIST_PVC)
    execute_job(backup_type=FULL_BACKUP, backend_type=S3)
    execute_job(backup_type=STATE_BACKUP, backend_type=LOCAL)
    execute_job(backup_type=STATE_BACKUP, backend_type=LOCAL_WITH_EXIST_PVC)
    execute_job(backup_type=STATE_BACKUP, backend_type=S3)
