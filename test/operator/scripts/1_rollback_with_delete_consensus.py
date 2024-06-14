import logging
import os
import sys
import time
from typing import List

from kubernetes import client, config
from tenacity import retry, stop_after_attempt, wait_fixed, after_log

sys.path.append("test/utils")
import util
from logger import logger


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
    old_bn = util.get_block_number()
    logger.info("the block number before rollback is: {}".format(old_bn))
    nodes = get_nodes(chain_name=os.getenv("CHAIN_NAME"), namespace=os.getenv("NAMESPACE"))
    # patch all nodes
    for node in nodes:
        patch_op_json = '''
        [
            {
                "op" : "replace" ,
                "path" : "/spec/template/spec/containers" ,
                "value" : [
                    {
                        "name": "patch-op",
                        "image": "registry.devops.rivtower.com/cita-cloud/cloud-op",
                        "command": [
                            "sleep",
                            "infinity"
                        ],
                        "imagePullPolicy": "Always",
                        env: [
                            {
                                "name": "AWS_REGION",
                                "value": "local"
                            }
                        ],
                        "volumeMounts": [
                            {
                                "mountPath": "/data",
                                "name": "datadir"
                            },
                            {
                                "mountPath": "/etc/cita-cloud/config",
                                "name": "node-config"
                            },
                            {
                                "mountPath": "/mnt",
                                "name": "node-account"
                            },
                            {
                                "mountPath": "/etc/localtime",
                                "name": "node-localtime"
                            }
                        ],
                        "workingDir": "/data"
                    }
                ]
            }
        ]
        '''
        result = util.exec("kubectl patch sts {} -n {} --type json --patch '{}'".format(node.name, os.getenv("NAMESPACE"), patch_op_json))
        if "patched" not in result:
            print("patch node error: ", result)
            exit(10)
    logger.info("all nodes patched")

    logger.info("wait 5min for all nodes restart")
    time.sleep(300)

    logger.info("rollback all nodes with delete consensus data")
    for node in nodes:
        result = util.exec_retry("kubectl exec -n {} -it {}-0 -c patch-op -- cloud-op rollback --clean -c /etc/cita-cloud/config/config.toml -n /data {}".format(os.getenv("NAMESPACE"), node.name, old_bn - 400))
        if "executor rollback done" not in result:
            print("exec rollback error: ", result)
            exit(20)
    logger.info("all nodes rollback")

    logger.info("rollback cloud storage")
    result = util.exec_retry("kubectl exec -n {} -it {}-0 -c patch-op -- cloud-op cloud-rollback -c /etc/cita-cloud/config/config.toml -n /data {}".format(os.getenv("NAMESPACE"), nodes[0].name, old_bn - 400))
    if "cloud rollback done" not in result:
        print("exec rollback error: ", result)
        exit(30)
    logger.info("cloud rollback")

    logger.info("undo all nodes")
    for node in nodes:
        result = util.exec("kubectl rollout undo -n {} sts {}".format(os.getenv("NAMESPACE"), node.name))
        if "rolled back" not in result:
            print("undo error: ", result)
            exit(40)
    
    logger.info("wait 5min for all nodes restart")
    time.sleep(300)

    for node in nodes:
        util.check_node_running(name=node.name, namespace=node.namespace)
    logger.info("all nodes running")

    logger.info("check rollback")
    node_status = util.get_node_status(retry_times=30, retry_wait=2)
    logger.debug("node status after rollback is: {}".format(node_status))

    init_height = node_status["init_block_number"]

    if init_height != old_bn - 400:
        raise Exception("rollback not excepted block number: init_height is:{} should be {}".format(init_height, old_bn - 400))
    
    new_bn = util.get_block_number()
    if new_bn  <= init_height:
        raise Exception("rollback not excepted block number: new_bn is:{} should be greater than {}".format(new_bn, init_height))

if __name__ == '__main__':
    main()
