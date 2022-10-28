import os
import sys
import time
from pprint import pprint

from kubernetes import client, config

from restore import Restore

sys.path.append("test/utils")
import util


class Backup(object):
    def __init__(self, name, namespace):
        config.load_kube_config()
        self.api = client.CustomObjectsApi()
        self.name = name
        self.namespace = namespace
        self.created = False

    def create(self, chain, node,
               deploy_method="cloud-config",
               storage_class="nas-client-provisioner",
               action="StopAndStart",
               image="registry.devops.rivtower.com/cita-cloud/cita-node-job:latest",
               pull_policy="Always",
               ttl=30,
               pod_affinity_flag=True):
        resource_body = {
            "apiVersion": "citacloud.rivtower.com/v1",
            "kind": "Backup",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "node": node,
                "deployMethod": deploy_method,
                "storageClass": storage_class,
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
            plural="backups",
            body=resource_body,
        )
        self.created = True

    def wait_job_complete(self):
        return util.wait_job_complete("backups", self.name, self.namespace)

    def delete(self):
        self.api.delete_namespaced_custom_object(
            group="citacloud.rivtower.com",
            version="v1",
            name=self.name,
            namespace=self.namespace,
            plural="backups",
            body=client.V1DeleteOptions(),
        )


if __name__ == "__main__":
    backup = Backup(name="sample-backup", namespace="cita")
    restore = Restore(name="sample-restore-for-backup", namespace="cita")
    try:
        # get block number when backup
        bn_with_backup = util.get_block_number()
        pprint("current block number is: {}".format(bn_with_backup))
        # create backup job
        backup.create(chain=os.getenv("CHAIN_NAME"),
                      node="{}-node0".format(os.getenv("CHAIN_NAME")))
        status = backup.wait_job_complete()
        if status == "Failed":
            raise Exception("backup exec failed")
        # check work well
        util.check_block_increase()
        pprint("create backup for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))

        # when difference > 200
        while True:
            if util.get_block_number() - bn_with_backup > 100:
                break
            pprint("waiting and exceeds the 100 block height at the time of backup...")
            time.sleep(2)
        # latest block number
        bn_with_latest = util.get_block_number()

        # create restore job
        restore.create_for_backup(chain=os.getenv("CHAIN_NAME"),
                                  node="{}-node0".format(os.getenv("CHAIN_NAME")),
                                  backup="sample-backup")
        status = restore.wait_job_complete()
        if status == "Failed":
            raise Exception("restore for backup exec failed")

        util.check_node_running(name="{}-node0".format(os.getenv("CHAIN_NAME")), namespace="cita")

        # check work well
        bn_with_recover = util.check_block_increase(retry_times=30, retry_wait=1, interval=2)

        if bn_with_recover > bn_with_latest:
            raise Exception("restore not excepted block number: bn_with_recover is {}, bn_with_latest is {}".
                            format(bn_with_recover, bn_with_latest))
        pprint("create restore for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))

    except Exception as e:
        pprint(e)
        exit(10)
    finally:
        if restore.created:
            restore.delete()
        if backup.created:
            backup.delete()
