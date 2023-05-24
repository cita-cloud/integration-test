import os
import sys
import time

import kubernetes.client.exceptions
from kubernetes import client, config

from restore import Restore

sys.path.append("test/utils")
import util
from logger import logger


class Backup(object):
    def __init__(self, name, namespace):
        config.load_kube_config()
        self.api = client.CustomObjectsApi()
        self.name = name
        self.namespace = namespace
        self.created = False

    def create(self, chain, node,
               deploy_method="cloud-config",
               storage_class="nfs-client",
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

    def clear(self):
        try:
            _ = self.api.get_namespaced_custom_object(
                group="citacloud.rivtower.com",
                version="v1",
                name=self.name,
                namespace=self.namespace,
                plural="backups",
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
            plural="backups",
        )
        if not resource.get('status'):
            return "No Status"
        return resource.get('status').get('status')


if __name__ == "__main__":
    backup = Backup(name="backup-{}".format(os.getenv("CHAIN_TYPE")), namespace=os.getenv("NAMESPACE"))
    backup.clear()
    restore = Restore(name="restore-for-backup-{}".format(os.getenv("CHAIN_TYPE")), namespace=os.getenv("NAMESPACE"))
    restore.clear()
    try:
        # get block number when backup
        bn_with_backup = util.get_block_number()
        logger.info("the block number before backup is: {}".format(bn_with_backup))
        # create backup job
        logger.info("create backup job...")
        backup.create(chain=os.getenv("CHAIN_NAME"),
                      node="{}-node0".format(os.getenv("CHAIN_NAME")))
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
        restore.create_for_backup(chain=os.getenv("CHAIN_NAME"),
                                  node="{}-node0".format(os.getenv("CHAIN_NAME")),
                                  backup=backup.name)
        status = restore.wait_job_complete()
        if status == "Failed":
            raise Exception("restore for backup exec failed")
        logger.info("the restore job for backup has been completed")

        util.check_node_running(name="{}-node0".format(os.getenv("CHAIN_NAME")), namespace=os.getenv("NAMESPACE"))
        
        init_time = int(time.time() * 1000)

        node_status = util.get_node_status(retry_times=30, retry_wait=2)
        logger.debug("node status after backup restore is: {}".format(node_status))

        bn_with_recover = node_status["self_status"]["height"]
        bn_init_height = node_status["init_block_number"]
        logger.info("the block number after backup restore is: {} init height is: {}".format(bn_with_recover, bn_init_height))

        if bn_init_height < bn_with_backup or bn_init_height > bn_with_recover:
            raise Exception("restore not excepted block number: bn_with_recover is {}, bn_init_height is {}, bn_with_backup is {}".
                            format(bn_with_recover, bn_init_height, bn_with_backup))

        while True:
            current_height = util.get_block_number()
            if current_height >= bn_with_latest:
                now_time = int(time.time() * 1000)
                logger.info("the sync speed is {:.2f} blocks/sec".format((current_height - bn_init_height) * 1000.0 / (now_time - init_time)))
                break
            time.sleep(1)

        logger.info(
            "create restore for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))
    except Exception as e:
        logger.exception(e)
        exit(10)
    finally:
        if restore.created and restore.status() == "Complete":
            restore.delete()
        if backup.created and backup.status() == "Complete":
            backup.delete()
