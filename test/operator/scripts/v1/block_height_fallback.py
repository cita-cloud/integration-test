import os
import sys

import kubernetes.client.exceptions
from kubernetes import client, config

sys.path.append("test/utils")
import util
from logger import logger


class BlockHeightFallback(object):
    def __init__(self, name, namespace):
        config.load_kube_config()
        self.api = client.CustomObjectsApi()
        self.name = name
        self.namespace = namespace
        self.created = False

    def create(self, chain, node, block_height,
               deploy_method="cloud-config",
               image="registry.devops.rivtower.com/cita-cloud/cita-node-job:latest",
               pull_policy="Always",
               ttl=30,
               pod_affinity_flag=True):
        resource_body = {
            "apiVersion": "citacloud.rivtower.com/v1",
            "kind": "BlockHeightFallback",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "blockHeight": block_height,
                "deployMethod": deploy_method,
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
            plural="blockheightfallbacks",
            body=resource_body,
        )
        self.created = True

    def wait_job_complete(self):
        return util.wait_job_complete("blockheightfallbacks", self.name, self.namespace)

    def delete(self):
        self.api.delete_namespaced_custom_object(
            group="citacloud.rivtower.com",
            version="v1",
            name=self.name,
            namespace=self.namespace,
            plural="blockheightfallbacks",
            body=client.V1DeleteOptions(),
        )

    def clear(self):
        try:
            _ = self.api.get_namespaced_custom_object(
                group="citacloud.rivtower.com",
                version="v1",
                name=self.name,
                namespace=self.namespace,
                plural="blockheightfallbacks",
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
            plural="blockheightfallbacks",
        )
        if not resource.get('status'):
            return "No Status"
        return resource.get('status').get('status')


if __name__ == "__main__":
    old_bn = util.get_block_number()
    logger.info("the block number before fallback is: {}".format(old_bn))
    bhf = BlockHeightFallback(name="bhf-{}".format(os.getenv("CHAIN_TYPE")), namespace="cita")
    bhf.clear()
    try:
        logger.info("create fallback job...")
        bhf.create(chain=os.getenv("CHAIN_NAME"),
                   node="{}-node0".format(os.getenv("CHAIN_NAME")),
                   block_height=5)
        status = bhf.wait_job_complete()
        if status == "Failed":
            raise Exception("block height fallback exec failed")
        logger.info("the fallback job has been completed")

        # check work well
        util.check_node_running(name="{}-node0".format(os.getenv("CHAIN_NAME")), namespace="cita")

        node_syncing_status = util.get_node_syncing_status(retry_times=30, retry_wait=3)
        logger.debug("node status after fallback is: {}".format(node_syncing_status))

        bn_with_bhf = node_syncing_status["self_status"]["height"]
        logger.info("the block number after fallback is: {}".format(bn_with_bhf))
        if bn_with_bhf >= old_bn:
            raise Exception(
                "block height fallback not excepted block number: bn_with_bhf is {}, old_bn is {}".format(bn_with_bhf,
                                                                                                          old_bn))
        logger.info("create block height fallback for node {}-node0 and check block increase successful".format(
            os.getenv("CHAIN_NAME")))
    except Exception as e:
        logger.exception(e)
        exit(20)
    finally:
        if bhf.created and bhf.status() == "Complete":
            bhf.delete()
