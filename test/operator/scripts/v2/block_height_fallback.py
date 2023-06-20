import os
import sys
import time

import kubernetes.client.exceptions
from kubernetes import client, config

from contants import BLOCK_HEIGHT_FOR_FALLBACK

sys.path.append("test/utils")
import util
from logger import logger


class BlockHeightFallback(object):
    def __init__(self, name, namespace):
        config.load_kube_config()
        self.custom_api = client.CustomObjectsApi()
        self.name = name
        self.namespace = namespace
        self.created = False

    def create(self,
               chain,
               node,
               block_height,
               deploy_method="cloud-config",
               action="StopAndStart"):
        resource_body = {
            "apiVersion": "rivtower.com/v1cita",
            "kind": "BlockHeightFallback",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "deployMethod": deploy_method,
                "action": action,
                "blockHeight": block_height
            },
        }
        # create a cluster scoped resource
        self.custom_api.create_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            namespace=self.namespace,
            plural="blockheightfallbacks",
            body=resource_body,
        )
        self.created = True

    def wait_job_complete(self):
        return util.wait_new_job_complete("blockheightfallbacks", self.name, self.namespace)

    def delete(self):
        self.custom_api.delete_namespaced_custom_object(
            group="rivtower.com",
            version="v1cita",
            name=self.name,
            namespace=self.namespace,
            plural="blockheightfallbacks",
            body=client.V1DeleteOptions(),
        )

    def clear(self):
        try:
            _ = self.custom_api.get_namespaced_custom_object(
                group="rivtower.com",
                version="v1cita",
                name=self.name,
                namespace=self.namespace,
                plural="blockheightfallbacks",
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
            plural="blockheightfallbacks",
        )
        if not resource.get('status'):
            return "No Status"
        for condition in resource.get('status').get('conditions'):
            if condition.get('type') == 'Completed':
                return condition.get('reason')


def create_block_height_fallback():
    old_bn = util.get_block_number()
    logger.info("the block number before fallback is: {}".format(old_bn))
    bhf = BlockHeightFallback(name="bhf-{}".format(os.getenv("CHAIN_TYPE")), namespace=os.getenv("NAMESPACE"))
    bhf.clear()
    try:
        logger.info("create fallback job...")
        bhf.create(chain=os.getenv("CHAIN_NAME"),
                   node="{}-node0".format(os.getenv("CHAIN_NAME")),
                   block_height=BLOCK_HEIGHT_FOR_FALLBACK)
        status = bhf.wait_job_complete()
        if status == "Failed":
            raise Exception("block height fallback exec failed")
        logger.info("the fallback job has been completed")

        # check work well
        util.check_node_running(name="{}-node0".format(os.getenv("CHAIN_NAME")), namespace=os.getenv("NAMESPACE"))

        init_time = int(time.time() * 1000)

        node_status = util.get_node_status(retry_times=30, retry_wait=3)
        logger.debug("node status after fallback is: {}".format(node_status))

        bn_with_bhf = node_status["self_status"]["height"]
        bn_init_height = node_status["init_block_number"]
        logger.info("the block number after fallback is: {} init height is: {}".format(bn_with_bhf, bn_init_height))
        if bn_init_height != BLOCK_HEIGHT_FOR_FALLBACK:
            raise Exception(
                "block height fallback not excepted block number: bn_with_bhf is {}, bn_init_height is:{} old_bn is {}".format(
                    bn_with_bhf, bn_init_height, old_bn))

        while True:
            current_height = util.get_block_number()
            if current_height >= old_bn:
                now_time = int(time.time() * 1000)
                logger.info("the sync speed is {:.2f} blocks/sec".format(
                    (current_height - bn_init_height) * 1000.0 / (now_time - init_time)))
                break
            time.sleep(1)

        logger.info("create block height fallback for node {}-node0 and check block increase successful".format(
            os.getenv("CHAIN_NAME")))
    except Exception as e:
        logger.exception(e)
        exit(20)
    finally:
        if bhf.created and bhf.status() == "Succeeded":
            bhf.delete()


if __name__ == '__main__':
    create_block_height_fallback()
