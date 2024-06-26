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
    
    logger.info("create backpvc")
    with open("backup_pvc.yaml", 'w') as pvc_file:
            pvc_file.write(''' 
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: {}-backup
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

    result = util.exec("kubectl apply -n {} -f backup_pvc.yaml".format(os.getenv("NAMESPACE")))
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
                            "mountPath": "/backup",
                            "name": "backup"
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
                "name": "backup",
                "persistentVolumeClaim": {
                    "claimName": "xxx-backup"
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

    logger.info("exec backup height {}".format(old_bn - 100))
    result = util.exec_retry("kubectl exec -n {} -it {}-node0-0 -c patch-op -- cloud-op backup -c /etc/cita-cloud/config/config.toml -n /data -p /backup {}".format(os.getenv("NAMESPACE"), os.getenv("CHAIN_NAME"), old_bn - 100))
    if "backup done!" not in result:
        print("exec back error: ", result)
        exit(20)

    logger.info("undo patch")
    result = util.exec("kubectl rollout undo -n {} sts {}-node0".format(os.getenv("NAMESPACE"), os.getenv("CHAIN_NAME")))
    if "rolled back" not in result:
        print("undo error: ", result)
        exit(30)
    
    logger.info("wait 5min for node0 restart after undo patch")
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
                "args": ["-c", "rm -rf /data/chain_data; rm -rf /data/data; cp -af /backup/nnn/chain_data /data; cp -af /backup/nnn/data /data"],
                "volumeMounts": [
                {
                    "mountPath": "/backup",
                    "name": "backup"
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
                "name": "backup",
                "persistentVolumeClaim": {
                "claimName": "xxx-backup"
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
    result = util.exec("kubectl run restore -n {} --overrides='{}' --image=registry.devops.rivtower.com/library/busybox:1.30 --restart=Never".format(os.getenv("NAMESPACE"), patch_json_template.replace("nnn", str(old_bn - 100)).replace("xxx", os.getenv("CHAIN_TYPE")).replace("zzz", os.getenv("CHAIN_NAME"))))
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

    logger.info("restart node0 after restore and wait 5min")
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

    if init_height != old_bn - 100:
        raise Exception("rollback not excepted block number: init_height is:{} should be {}".format(init_height, old_bn - 100))
