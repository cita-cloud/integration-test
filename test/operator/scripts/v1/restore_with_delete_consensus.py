import logging
import os
import sys
from typing import List

from kubernetes import client, config
from tenacity import retry, stop_after_attempt, wait_fixed, after_log

sys.path.append("test/utils")
import util
from logger import logger

from restore import Restore


class Node(object):
    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name
        config.load_kube_config()
        self.apps_v1 = client.AppsV1Api()

    def stop(self):
        body = {
            'spec': {
                'replicas': 0,
            }
        }
        self.apps_v1.patch_namespaced_stateful_set_scale(self.name, self.namespace, body)

    def start(self):
        body = {
            'spec': {
                'replicas': 1,
            }
        }
        self.apps_v1.patch_namespaced_stateful_set_scale(self.name, self.namespace, body)

    @retry(stop=stop_after_attempt(150), wait=wait_fixed(2), after=after_log(logger, logging.DEBUG))
    def check_stopped(self):
        sts = self.apps_v1.read_namespaced_stateful_set(self.name, self.namespace)
        if sts.status.replicas != 0:
            raise Exception("the node {}/{} is still running".format(self.namespace, self.name))


def get_nodes(chain_name: str, namespace: str) -> List[Node]:
    nodes = []
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    label_selector = f"app.kubernetes.io/chain-name={chain_name}"
    ret = apps_v1.list_namespaced_stateful_set(namespace=namespace, label_selector=label_selector)
    for sts in ret.items:
        node = Node(namespace=namespace, name=sts.metadata.name)
        nodes.append(node)
    return nodes


def main():
    nodes = get_nodes(chain_name=os.getenv("CHAIN_NAME"), namespace=os.getenv("NAMESPACE"))
    # stop all nodes
    for node in nodes:
        node.stop()
        node.check_stopped()
    logger.info("all nodes stopped")

    # restore all nodes
    for node in nodes:
        restore = Restore(namespace=node.namespace, name="delete-consensus-restore-{}".format(node.name))
        restore.clear()
        restore.create_for_backup(chain=os.getenv("CHAIN_NAME"),
                                  node=node.name,
                                  backup="backup-{}".format(os.getenv("CHAIN_TYPE")),
                                  action="Direct",
                                  delete_consensus_data=True)
        status = restore.wait_job_complete()
        if status == "Failed":
            raise Exception("restore for backup exec failed")
        logger.info("the restore job [] for backup has been completed".format(restore.name))

    for node in nodes:
        node.start()
    for node in nodes:
        util.check_node_running(name=node.name, namespace=node.namespace)
    logger.info("all nodes running")


if __name__ == '__main__':
    main()
