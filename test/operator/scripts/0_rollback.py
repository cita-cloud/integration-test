import os
import sys
import time

import kubernetes.client.exceptions
from kubernetes import client, config

sys.path.append("test/utils")
import util
from logger import logger

if __name__ == "__main__":
    old_bn = util.get_block_number()
    logger.info("the block number before rollback is: {}".format(old_bn))
    
    # patch node
    patch_op_json = '''[
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
    ]'''
    patch_op_cmd = "kubectl patch sts {}-node0 -n {} --type json --patch '{}'".format(os.getenv("CHAIN_NAME"), os.getenv("NAMESPACE"), patch_op_json)
    result = util.exec(patch_op_cmd)
    if "patched" not in result:
        print("patch node error: ", result)
        exit(10)
    
    # wait for node restart
    time.sleep(300)
    util.check_node_running(name="{}-node0".format(os.getenv("CHAIN_NAME")), namespace=os.getenv("NAMESPACE"))

    # exec rollback
    result = util.exec("kubectl exec -n {} -it {}-node0-0 -c patch-op -- cloud-op rollback -c /etc/cita-cloud/config/config.toml -n /data {}".format(os.getenv("NAMESPACE"), os.getenv("CHAIN_NAME"), old_bn - 100))
    if "executor rollback done" not in result:
        print("exec rollback error: ", result)
        exit(20)

    # undo patch
    result = util.exec("kubectl rollout undo -n {} sts {}-node0".format(os.getenv("NAMESPACE"), os.getenv("CHAIN_NAME")))
    if "rolled back" not in result:
        print("undo error: ", result)
        exit(30)
    
    # wait for node restart
    time.sleep(300)
    util.check_block_increase()

    # check rollback
    node_status = util.get_node_status(retry_times=30, retry_wait=2)
    logger.debug("node status after rollback is: {}".format(node_status))

    init_height = node_status["init_block_number"]

    if init_height != old_bn - 100:
        raise Exception("rollback not excepted block number: init_height is:{} should be {}".format(init_height, old_bn - 100))
    
    new_bn = util.get_block_number()
    if new_bn <= old_bn:
        raise Exception("rollback not excepted block number: new_bn is:{} should be greater than {}".format(new_bn, old_bn))