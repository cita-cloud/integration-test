import os
import sys
import time
from pprint import pprint

from kubernetes import client, config

from restore import Restore

sys.path.append("test/utils")
import util


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
               image="registry.devops.rivtower.com/cita-cloud/cita-node-job:v0.0.2",
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
    snapshot = Snapshot(name="sample-snapshot", namespace="cita")
    restore = Restore(name="sample-restore-for-snapshot", namespace="cita")
    try:
        # create snapshot job
        snapshot.create(chain=os.getenv("CHAIN_NAME"),
                        node="{}-node0".format(os.getenv("CHAIN_NAME")),
                        block_height=5,
                        ttl=120)
        status = snapshot.wait_job_complete()
        if status == "Failed":
            raise Exception("snapshot exec failed")
        # check work well
        util.check_block_increase()
        pprint("create snapshot for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))

        # util current block number > 150, continue
        while True:
            if util.get_block_number() > 150:
                break
            pprint("waiting for the current block height to be 150...")
            time.sleep(2)

        # latest block number
        bn_with_latest = util.get_block_number()

        # create restore job
        restore.create_for_snapshot(chain=os.getenv("CHAIN_NAME"),
                                    node="{}-node0".format(os.getenv("CHAIN_NAME")),
                                    snapshot="sample-snapshot")
        status = restore.wait_job_complete()
        if status == "Failed":
            raise Exception("restore for snapshot exec failed")

        util.check_node_running(name="{}-node0".format(os.getenv("CHAIN_NAME")), namespace="cita")

        # check work well
        bn_with_recover = util.check_block_increase(retry_times=30, retry_wait=1, interval=2)
        if bn_with_recover > bn_with_latest:
            raise Exception("snapshot not excepted block number: bn_with_recover is {}, bn_with_latest is {}".format(
                bn_with_recover, bn_with_latest))
        pprint("create restore for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))

    except Exception as e:
        pprint(e)
        exit(30)
    finally:
        if restore.created:
            restore.delete()
        if snapshot.created:
            snapshot.delete()
