import os
import sys

from kubernetes import client, config

sys.path.append("test/utils")
import util
from logger import logger


class Switchover(object):
    def __init__(self, name, namespace):
        config.load_kube_config()
        self.api = client.CustomObjectsApi()
        self.name = name
        self.namespace = namespace
        self.created = False

    def create(self, chain, source_node, dest_node,
               image="registry.devops.rivtower.com/cita-cloud/cita-node-job:latest",
               pull_policy="Always",
               ttl=30):
        resource_body = {
            "apiVersion": "citacloud.rivtower.com/v1",
            "kind": "Switchover",
            "metadata": {"name": self.name},
            "spec": {
                "chain": chain,
                "sourceNode": source_node,
                "destNode": dest_node,
                "pullPolicy": pull_policy,
                "image": image,
                "ttlSecondsAfterFinished": ttl
            },
        }

        # create a cluster scoped resource
        self.api.create_namespaced_custom_object(
            group="citacloud.rivtower.com",
            version="v1",
            namespace=self.namespace,
            plural="switchovers",
            body=resource_body,
        )
        self.created = True

    def delete(self):
        self.api.delete_namespaced_custom_object(
            group="citacloud.rivtower.com",
            version="v1",
            name=self.name,
            namespace=self.namespace,
            plural="switchovers",
            body=client.V1DeleteOptions(),
        )

    def wait_job_complete(self):
        return util.wait_job_complete("switchovers", self.name, self.namespace)


def check_node_account_switched(namespace, name, wanted_account_name):
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    exist = False
    node_sts = apps_v1.read_namespaced_stateful_set(name=name, namespace=namespace)
    for volume in node_sts.spec.template.spec.volumes:
        if volume.config_map.name == wanted_account_name:
            exist = True
    return exist


if __name__ == "__main__":
    sw0 = Switchover(name="switchover-{}-0".format(os.getenv("CHAIN_TYPE")), namespace="cita")
    sw1 = Switchover(name="switchover-{}-1".format(os.getenv("CHAIN_TYPE")), namespace="cita")
    try:
        logger.info("create switchover job, [node0 update to node1-account, node1 update to node0-account]...")
        sw0.create(chain=os.getenv("CHAIN_NAME"),
                   source_node="{}-node0".format(os.getenv("CHAIN_NAME")),
                   dest_node="{}-node1".format(os.getenv("CHAIN_NAME")))
        status = sw0.wait_job_complete()
        if status == "Failed":
            raise Exception("switchover exec failed")
        logger.info("the switchover job has been completed")
        if not check_node_account_switched(namespace="cita",
                                           name="{}-node0".format(os.getenv("CHAIN_NAME")),
                                           wanted_account_name="{}-node1-account".format(
                                               os.getenv("CHAIN_NAME"))) or not \
                check_node_account_switched(namespace="cita",
                                            name="{}-node1".format(os.getenv("CHAIN_NAME")),
                                            wanted_account_name="{}-node0-account".format(os.getenv("CHAIN_NAME"))):
            raise Exception("account configmap haven't switched")
        # check work well
        util.check_block_increase()
        logger.info(
            "create switchover for [node0 update to node1-account && node1 update to node0-account] "
            "and check block increase successful")

        logger.info("create switchover job, [node0 update to node0-account, node1 update to node1-account]...")
        sw1.create(chain=os.getenv("CHAIN_NAME"),
                   source_node="{}-node0".format(os.getenv("CHAIN_NAME")),
                   dest_node="{}-node1".format(os.getenv("CHAIN_NAME")))
        status = sw1.wait_job_complete()
        if status == "Failed":
            raise Exception("switchover exec failed")
        logger.info("the switchover job has been completed")
        if not check_node_account_switched(namespace="cita",
                                           name="{}-node0".format(os.getenv("CHAIN_NAME")),
                                           wanted_account_name="{}-node0-account".format(
                                               os.getenv("CHAIN_NAME"))) or not \
                check_node_account_switched(namespace="cita",
                                            name="{}-node1".format(os.getenv("CHAIN_NAME")),
                                            wanted_account_name="{}-node1-account".format(os.getenv("CHAIN_NAME"))):
            raise Exception("account configmap haven't switched")
        # check work well
        util.check_block_increase()
        logger.info(
            "create switchover for [node0 update to node0-account && node1 update to node1-account] "
            "and check block increase successful")
    except Exception as e:
        logger.exception(e)
        exit(40)
    finally:
        if sw0.created:
            sw0.delete()
        if sw1.created:
            sw1.delete()
