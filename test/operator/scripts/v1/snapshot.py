import os
import sys
import time

from kubernetes import client, config

from restore import Restore

sys.path.append("test/utils")
import util
from logger import logger


class Snapshot(object):
    def __init__(self, name, namespace):
        config.load_kube_config()
        self.api = client.CustomObjectsApi()
        self.name = name
        self.namespace = namespace
        self.created = False

    def create(self, chain, node, block_height,
               deploy_method="cloud-config",
               storage_class="nas-client-provisioner",
               image="registry.devops.rivtower.com/cita-cloud/cita-node-job:latest",
               pull_policy="Always",
               ttl=30,
               pod_affinity_flag=True):
        resource_body = {
            "apiVersion": "citacloud.rivtower.com/v1",
            "kind": "Snapshot",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "blockHeight": block_height,
                "deployMethod": deploy_method,
                "storageClass": storage_class,
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
            plural="snapshots",
            body=resource_body,
        )
        self.created = True

    def wait_job_complete(self):
        return util.wait_job_complete("snapshots", self.name, self.namespace)

    def delete(self):
        self.api.delete_namespaced_custom_object(
            group="citacloud.rivtower.com",
            version="v1",
            name=self.name,
            namespace=self.namespace,
            plural="snapshots",
            body=client.V1DeleteOptions(),
        )


if __name__ == "__main__":
    snapshot = Snapshot(name="snapshot-{}".format(os.getenv("CHAIN_TYPE")), namespace="cita")
    restore = Restore(name="restore-for-snapshot-{}".format(os.getenv("CHAIN_TYPE")), namespace="cita")
    try:
        # create snapshot job
        logger.info("create snapshot job...")
        snapshot.create(chain=os.getenv("CHAIN_NAME"),
                        node="{}-node0".format(os.getenv("CHAIN_NAME")),
                        block_height=5,
                        ttl=120)
        status = snapshot.wait_job_complete()
        if status == "Failed":
            raise Exception("snapshot exec failed")
        logger.info("the snapshot job has been completed")
        # check work well
        util.check_block_increase()
        logger.info(
            "create snapshot for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))

        # util current block number > 150, continue
        while True:
            now_bn = util.get_block_number()
            if now_bn > 150:
                break
            logger.info("waiting for the current block height to be 150, current block number: {}...".format(now_bn))
            time.sleep(2)

        # latest block number
        bn_with_latest = util.get_block_number()
        logger.info("the latest block number after waiting is: {}".format(bn_with_latest))

        # create restore job
        logger.info("create restore job for snapshot...")
        restore.create_for_snapshot(chain=os.getenv("CHAIN_NAME"),
                                    node="{}-node0".format(os.getenv("CHAIN_NAME")),
                                    snapshot=snapshot.name)
        status = restore.wait_job_complete()
        if status == "Failed":
            raise Exception("restore for snapshot exec failed")
        logger.info("the restore job for snapshot has been completed")

        util.check_node_running(name="{}-node0".format(os.getenv("CHAIN_NAME")), namespace="cita")

        node_syncing_status = util.get_node_syncing_status(retry_times=30, retry_wait=3)
        logger.debug("node status after snapshot restore is: {}".format(node_syncing_status))

        bn_with_recover = node_syncing_status["self_status"]["height"]
        logger.info("the block number after snapshot restore is: {}".format(bn_with_recover))
        if bn_with_recover > bn_with_latest:
            raise Exception("snapshot not excepted block number: bn_with_recover is {}, bn_with_latest is {}".format(
                bn_with_recover, bn_with_latest))

        logger.info(
            "create restore for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))

        # wait for the consensus block to determine whether the node is ok
        util.wait_block_number_exceed_specified_height(specified_height=bn_with_latest, retry_times=100, retry_wait=2)

    except Exception as e:
        logger.exception(e)
        exit(30)
    finally:
        if restore.created:
            restore.delete()
        if snapshot.created:
            snapshot.delete()
