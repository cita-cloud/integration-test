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

import os
import sys

import kubernetes.client.exceptions
from kubernetes import client, config

from bucket import BucketConfig
from contants import BACKUP_REPO_SECRET, BACKUP_REPO_SECRET_KEY, MINIO_CREDENTIALS_SECRET, \
    MINIO_CREDENTIALS_SECRET_ACCESS_KEY, MINIO_CREDENTIALS_SECRET_SECRET_KEY, MINIO_CREDENTIALS_SECRET_ACCESS_VALUE, \
    MINIO_CREDENTIALS_SECRET_SECRET_VALUE, BUCKET_ENDPOINT, BUCKET_NAME

sys.path.append("test/utils")
import util
from logger import logger


class Prune(object):
    def __init__(self, name, namespace):
        config.load_kube_config()
        self.api = client.CustomObjectsApi()
        self.name = name
        self.namespace = namespace
        self.created = False

    def create(self,
               chain,
               node,
               bucket_config: BucketConfig = None):
        resource_body = {
            "apiVersion": "rivtower.com/v1cita",
            "kind": "Prune",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "retention": {
                    "keepLast": 0,
                    "keepDaily": 14
                },
                "backend": {
                    "repoPasswordSecretRef": {
                        "name": BACKUP_REPO_SECRET,
                        "key": BACKUP_REPO_SECRET_KEY,
                    },
                    "s3": {
                        "endpoint": "http://" + bucket_config.endpoint,
                        "bucket": bucket_config.name,
                        "accessKeyIDSecretRef": {
                            "name": MINIO_CREDENTIALS_SECRET,
                            "key": MINIO_CREDENTIALS_SECRET_ACCESS_KEY
                        },
                        "secretAccessKeySecretRef": {
                            "name": MINIO_CREDENTIALS_SECRET,
                            "key": MINIO_CREDENTIALS_SECRET_SECRET_KEY,
                        },
                    },
                },
            },
        }
        # create a cluster scoped resource
        self.api.create_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            namespace=self.namespace,
            plural="prunes",
            body=resource_body,
        )
        self.created = True

    def wait_job_complete(self):
        return util.wait_new_job_complete("prunes", self.name, self.namespace)

    def delete(self):
        self.api.delete_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            name=self.name,
            namespace=self.namespace,
            plural="prunes",
            body=client.V1DeleteOptions(),
        )

    def clear(self):
        try:
            _ = self.api.get_namespaced_custom_object(
                group="rivtower.com",
                version="v1cita",
                name=self.name,
                namespace=self.namespace,
                plural="prunes",
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
            plural="prunes",
        )
        if not resource.get('status'):
            return "No Status"
        for condition in resource.get('status').get('conditions'):
            if condition.get('type') == 'Completed':
                return condition.get('reason')


if __name__ == '__main__':
    prune = Prune(namespace=os.getenv("NAMESPACE"), name="prune-{}".format(os.getenv("CHAIN_TYPE")))
    prune.clear()
    bucket_cfg = BucketConfig(name=BUCKET_NAME,
                              endpoint=BUCKET_ENDPOINT,
                              access_key=MINIO_CREDENTIALS_SECRET_ACCESS_VALUE,
                              secret_key=MINIO_CREDENTIALS_SECRET_SECRET_VALUE)
    try:
        logger.debug("========================>")
        logger.debug("exec prune...")
        logger.debug("========================>")

        prune.create(chain=os.getenv("CHAIN_NAME"), node="{}-node0".format(os.getenv("CHAIN_NAME")),
                     bucket_config=bucket_cfg)

        status = prune.wait_job_complete()
        if status == "Failed":
            raise Exception("prune exec failed")
        logger.info("the prune job has been completed")
    except Exception as s:
        logger.exception(s)
        exit(10)
    finally:
        logger.debug("<========================")
        logger.debug("exec prune finally...")
        logger.debug("<========================")
        if prune.created and prune.status() == "Succeeded":
            prune.delete()
