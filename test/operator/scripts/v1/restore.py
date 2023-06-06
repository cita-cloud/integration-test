import sys

import kubernetes.client.exceptions
from kubernetes import client, config

sys.path.append("test/utils")
import util
from logger import logger


class Restore(object):
    def __init__(self, name, namespace):
        config.load_kube_config()
        self.api = client.CustomObjectsApi()
        self.name = name
        self.namespace = namespace
        self.created = False

    def create_for_backup(self, chain, node,
                          backup,
                          deploy_method="cloud-config",
                          action="StopAndStart",
                          image="registry.devops.rivtower.com/cita-cloud/cita-node-job:latest",
                          pull_policy="Always",
                          ttl=30,
                          pod_affinity_flag=True,
                          delete_consensus_data=False):
        resource_body = {
            "apiVersion": "citacloud.rivtower.com/v1",
            "kind": "Restore",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "deployMethod": deploy_method,
                "backup": backup,
                "action": action,
                "pullPolicy": pull_policy,
                "image": image,
                "ttlSecondsAfterFinished": ttl,
                "podAffinityFlag": pod_affinity_flag,
                "deleteConsensusData": delete_consensus_data,
            },
        }
        # create a cluster scoped resource
        self.api.create_namespaced_custom_object(
            group="citacloud.rivtower.com",
            version="v1",
            namespace=self.namespace,
            plural="restores",
            body=resource_body,
        )
        self.created = True

    def create_for_snapshot(self, chain, node,
                            snapshot,
                            deploy_method="cloud-config",
                            action="StopAndStart",
                            image="registry.devops.rivtower.com/cita-cloud/cita-node-job:latest",
                            pull_policy="Always",
                            ttl=30,
                            pod_affinity_flag=True):
        resource_body = {
            "apiVersion": "citacloud.rivtower.com/v1",
            "kind": "Restore",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "deployMethod": deploy_method,
                "snapshot": snapshot,
                "action": action,
                "pullPolicy": pull_policy,
                "image": image,
                "ttlSecondsAfterFinished": ttl,
                "podAffinityFlag": pod_affinity_flag,
            },
        }
        # create a cluster scoped resource
        self.api.create_namespaced_custom_object(
            group="citacloud.rivtower.com",
            version="v1",
            namespace=self.namespace,
            plural="restores",
            body=resource_body,
        )
        self.created = True

    def wait_job_complete(self):
        return util.wait_job_complete("restores", self.name, self.namespace)

    def delete(self):
        self.api.delete_namespaced_custom_object(
            group="citacloud.rivtower.com",
            version="v1",
            name=self.name,
            namespace=self.namespace,
            plural="restores",
            body=client.V1DeleteOptions(),
        )

    def clear(self):
        try:
            _ = self.api.get_namespaced_custom_object(
                group="citacloud.rivtower.com",
                version="v1",
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
            group="citacloud.rivtower.com",
            version="v1",
            name=self.name,
            namespace=self.namespace,
            plural="restores",
        )
        if not resource.get('status'):
            return "No Status"
        return resource.get('status').get('status')
