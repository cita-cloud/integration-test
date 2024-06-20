import os
import sys
import time

import kubernetes.client.exceptions
from kubernetes import client, config

sys.path.append("test/utils")
import util
from logger import logger

if __name__ == "__main__":
    if os.getenv("CHAIN_TYPE") == "overlord":
        print("overlord chain don't need to execute this test")
        exit(0)
    
    old_bn = util.get_block_number()
    logger.info("the block number before backup is: {}".format(old_bn))

    logger.info("create export pvc")
    with open("export_pvc.yaml", 'w') as pvc_file:
            pvc_file.write(''' 
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: {}-export
      labels:
        app.kubernetes.io/chain-name: {}
    spec:
      storageClassName: {}
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 10G
    '''.format(os.getenv("CHAIN_TYPE"), os.getenv("CHAIN_NAME"), os.getenv("SC")))

    result = util.exec("kubectl apply -n {} -f export_pvc.yaml".format(os.getenv("NAMESPACE")))
    if "created" not in result:
        print("create pvc error: ", result)
        exit(10)

    logger.info("patch node0")
    # xxx --- chain type
    patch_op_json_template = '''
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
                    "env": [
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
                        },
                        {
                            "mountPath": "/export",
                            "name": "export"
                        }
                    ],
                    "workingDir": "/data"
                }
            ]
        },
        {
            "op" : "add" ,
            "path" : "/spec/template/spec/volumes/-" ,
            "value" : {
                "name": "export",
                "persistentVolumeClaim": {
                    "claimName": "xxx-export"
                }
            }
        }
    ]
    '''
    result = util.exec("kubectl patch sts {}-node0 -n {} --type json --patch '{}'".format(os.getenv("CHAIN_NAME"), os.getenv("NAMESPACE"), patch_op_json_template.replace("xxx", os.getenv("CHAIN_TYPE"))))
    if "patched" not in result:
        print("patch node error: ", result)
        exit(10)

    logger.info("wait 5min for node0 restart after patch")
    time.sleep(300)
    util.check_node_running(name="{}-node0".format(os.getenv("CHAIN_NAME")), namespace=os.getenv("NAMESPACE"))

    logger.info("exec export")
    result = util.exec_retry("kubectl exec -n {} -it {}-node0-0 -c patch-op -- cloud-op export -c /etc/cita-cloud/config/config.toml -n /data -p /export -b 0 -e 200".format(os.getenv("NAMESPACE"), os.getenv("CHAIN_NAME")))
    if "export done!" not in result:
        print("exec export error: ", result)
        exit(20)

    logger.info("exec incremental export")
    result = util.exec_retry("kubectl exec -n {} -it {}-node0-0 -c patch-op -- cloud-op export -c /etc/cita-cloud/config/config.toml -n /data -p /export -b 201 -e 300".format(os.getenv("NAMESPACE"), os.getenv("CHAIN_NAME")))
    if "export done!" not in result:
        print("exec incremental export error: ", result)
        exit(20)

    logger.info("undo patch")
    result = util.exec("kubectl rollout undo -n {} sts {}-node0".format(os.getenv("NAMESPACE"), os.getenv("CHAIN_NAME")))
    if "rolled back" not in result:
        print("undo error: ", result)
        exit(30)

    logger.info("wait 5min for node0 restart")
    time.sleep(300)
    util.check_block_increase()

    # restore
    logger.info("stop node0")
    result = util.exec("kubectl scale sts {}-node0 -n {} --replicas=0".format(os.getenv("CHAIN_NAME"), os.getenv("NAMESPACE")))
    if "scaled" not in result:
        print("stop node error: ", result)
        exit(40)

    logger.info("wait 5min for node0 stop")
    time.sleep(300)

    logger.info("create temp pod")
    # nnn --- backup height
    # xxx --- chain type
    # zzz --- chain name
    patch_json_template = '''
    {
        "spec": {
            "containers": [
            {
                "name": "restore",
                "image": "registry.devops.rivtower.com/library/busybox:1.30",
                "command": ["/bin/sh"],
                "args": ["-c", "rm -rf /data/chain_data; rm -rf /data/data; cp -af /export/chain_data /data; cp -af /export/data /data"],
                "volumeMounts": [
                {
                    "mountPath": "/export",
                    "name": "export"
                },
                {
                    "mountPath": "/data",
                    "name": "data"
                }
                ]
            }
            ],
            "volumes": [
            {
                "name": "export",
                "persistentVolumeClaim": {
                "claimName": "xxx-export"
                }
            },
            {
                "name": "data",
                "persistentVolumeClaim": {
                "claimName": "datadir-zzz-node0-0"
                }
            }
            ]
        }
    }
    '''
    result = util.exec("kubectl run restore -n {} --overrides='{}' --image=registry.devops.rivtower.com/library/busybox:1.30 --restart=Never".format(os.getenv("NAMESPACE"), patch_json_template.replace("xxx", os.getenv("CHAIN_TYPE")).replace("zzz", os.getenv("CHAIN_NAME"))))
    if "created" not in result:
        print("create temp pod error: ", result)
        exit(50)

    logger.info("wait 5min for restore finish")
    time.sleep(300)

    logger.info("delete temp pod")
    result = util.exec("kubectl delete pod restore -n {}".format(os.getenv("NAMESPACE")))
    if "deleted" not in result:
        print("delete temp pod error: ", result)
        exit(60)
    time.sleep(60)

    logger.info("restart node0 and wait 5min")
    result = util.exec("kubectl scale sts {}-node0 -n {} --replicas=1".format(os.getenv("CHAIN_NAME"), os.getenv("NAMESPACE")))
    if "scaled" not in result:
        print("stop node error: ", result)
        exit(70)
    time.sleep(300)

    util.check_block_increase()

    logger.info("check restore")
    node_status = util.get_node_status(retry_times=30, retry_wait=2)
    logger.debug("node status after restore is: {}".format(node_status))

    init_height = node_status["init_block_number"]

    if init_height != 300:
        raise Exception("rollback not excepted block number: init_height is:{} should be 300".format(init_height))
