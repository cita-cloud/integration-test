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

import logging
import os
import sys

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from tenacity import retry, stop_after_attempt, wait_fixed, after_log

sys.path.append("test/utils")
from logger import logger


class Pvc(object):
    def __init__(self, namespace, name):
        config.load_kube_config()
        self.namespace = namespace
        self.name = name
        self.core_api = client.CoreV1Api()

    def create(self, storage_class="nas-client-provisioner", size="10Gi"):
        pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": self.name,
            },
            "spec": {
                "accessModes": [
                    "ReadWriteOnce"
                ],
                "storageClassName": storage_class,
                "resources": {
                    "requests": {
                        "storage": size
                    }
                }
            }
        }
        self.core_api.create_namespaced_persistent_volume_claim(
            self.namespace,
            pvc
        )

    def exist(self):
        try:
            self.core_api.read_namespaced_persistent_volume_claim(self.name, self.namespace)
        except ApiException:
            return False
        return True

    @retry(stop=stop_after_attempt(60), wait=wait_fixed(3), after=after_log(logger, logging.DEBUG))
    def check_pvc_deleted(self):
        try:
            self.core_api.read_namespaced_persistent_volume_claim(self.name, self.namespace)
        except ApiException:
            return True
        raise Exception("the pvc is still exist")

    def delete(self):
        self.core_api.delete_namespaced_persistent_volume_claim(self.name, self.namespace)


def prepare_pvc():
    pvc = Pvc(namespace=os.getenv("NAMESPACE"), name="integration-test-pvc")
    if pvc.exist():
        pvc.delete()
        pvc.check_pvc_deleted()
        pvc.create()
    else:
        pvc.create()


if __name__ == '__main__':
    # prepare_pvc()
    pass
