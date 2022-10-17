import os
import sys
from pprint import pprint

from kubernetes import client, config
from tenacity import retry, stop_after_attempt, wait_fixed

sys.path.append("test/utils")
import util

apply_cmd = "kubectl apply -f {}"
delete_cmd = "kubectl delete -f {}"


def create_backup(name, namespace):
    config.load_kube_config()
    api = client.CustomObjectsApi()
    resource_body = {
        "apiVersion": "citacloud.rivtower.com/v1",
        "kind": "Backup",
        "metadata": {"name": name},
        "spec": {
            "chain": "{}".format(os.getenv("CHAIN_NAME")),
            "node": "{}-node0".format(os.getenv("CHAIN_NAME")),
            "deployMethod": "cloud-config",
            "storageClass": "nas-client-provisioner",
            "pullPolicy": "Always",
            "image": "registry.devops.rivtower.com/cita-cloud/cita-node-job:v0.0.2",
            "podAffinityFlag": True,
        },
    }
    # create a cluster scoped resource
    api.create_namespaced_custom_object(
        group="citacloud.rivtower.com",
        version="v1",
        namespace=namespace,
        plural="backups",
        body=resource_body,
    )

    try:
        status = wait_job_complete("backups", name, namespace)
        if status == "Failed":
            pprint("backup exec failed")
            exit(10)
    except Exception as e:
        pprint(e)
        exit(20)

    # check work well
    util.check_block_increase()
    pprint("create backup for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))


@retry(stop=stop_after_attempt(30), wait=wait_fixed(2))
def wait_job_complete(crd, cr_name, namespace):
    config.load_kube_config()
    api = client.CustomObjectsApi()
    resource = api.get_namespaced_custom_object(
        group="citacloud.rivtower.com",
        version="v1",
        name=cr_name,
        namespace=namespace,
        plural=crd,
    )
    if not resource.get('status'):
        raise Exception("no status")
    if resource.get('status').get('status') == 'Active':
        raise Exception("status not complete")
    return resource.get('status').get('status')


def create_restore(name, namespace, backup_name):
    config.load_kube_config()
    api = client.CustomObjectsApi()
    resource_body = {
        "apiVersion": "citacloud.rivtower.com/v1",
        "kind": "Restore",
        "metadata": {"name": name},
        "spec": {
            "chain": "{}".format(os.getenv("CHAIN_NAME")),
            "node": "{}-node0".format(os.getenv("CHAIN_NAME")),
            "deployMethod": "cloud-config",
            "backup": backup_name,
            "pullPolicy": "Always",
            "image": "registry.devops.rivtower.com/cita-cloud/cita-node-job:v0.0.2",
            "podAffinityFlag": True,
        },
    }
    # create a cluster scoped resource
    api.create_namespaced_custom_object(
        group="citacloud.rivtower.com",
        version="v1",
        namespace=namespace,
        plural="restores",
        body=resource_body,
    )

    try:
        status = wait_job_complete("restores", name, namespace)
        if status == "Failed":
            pprint("backup exec failed")
            exit(30)
    except Exception as e:
        pprint(e)
        exit(40)

    # check work well
    util.check_block_increase()
    pprint("create restore for node {}-node0 and check block increase successful".format(os.getenv("CHAIN_NAME")))


if __name__ == "__main__":
    create_backup(name="sample-backup", namespace="cita")
    create_restore(name="sample-restore", namespace="cita", backup_name="sample-backup")
