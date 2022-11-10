#!/usr/bin/env python
#
# Copyright Rivtower Technologies LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import subprocess
import time

from kubernetes import client, config
from tenacity import retry, stop_after_attempt, wait_fixed, after_log

from logger import logger

retry_times = 5
DEFAULT_RETRY_TIMES = 5
retry_wait = 10
DEFAULT_RETRY_WAIT = 10
DEFAULT_INTERVAL = 30

get_receipt_fmt = 'cldi -c default get receipt {}'
get_abi_fmt = 'cldi -c default get abi {}'
get_tx_fmt = 'cldi -c default get tx {}'
get_block_fmt = "cldi -c default get block {}"


def get_block_number(retry_times=DEFAULT_RETRY_TIMES, retry_wait=DEFAULT_RETRY_WAIT):
    @retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
    def inner_func():
        return int(subprocess.getoutput("cldi -c default get block-number"))

    return inner_func()


def check_block_increase(retry_times=DEFAULT_RETRY_TIMES, retry_wait=DEFAULT_RETRY_WAIT, interval=DEFAULT_INTERVAL):
    @retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
    def inner_func():
        old = get_block_number(retry_times=retry_times, retry_wait=retry_wait)
        time.sleep(interval)
        new = get_block_number(retry_times=retry_times, retry_wait=retry_wait)
        if new == old:
            raise Exception('block not increase!')
        return new

    return inner_func()


@retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
def get_node_block_number(node):
    get_node_block_fmt = 'cldi -c {} get block-number'
    return int(subprocess.getoutput(get_node_block_fmt.format(node)))


@retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
def check_node_block_increase(node):
    old = get_node_block_number(node)
    time.sleep(30)
    new = get_node_block_number(node)
    if new == old:
        raise Exception('{} block not increase!'.format(node))


@retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
def get_receipt(tx_hash):
    result = subprocess.getoutput(get_receipt_fmt.format(tx_hash))
    if result.__contains__("Error"):
        raise Exception('get receipt failed!')
    return result


@retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
def get_tx(tx_hash):
    result = subprocess.getoutput(get_tx_fmt.format(tx_hash))
    if result.__contains__("Error"):
        raise Exception('get tx failed!')
    tx = json.loads(result)
    if tx['height'] == 18446744073709551615:
        raise Exception('tx in pool!')
    return result


@retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
def get_node_tx(node, tx_hash):
    result = subprocess.getoutput('cldi -c {} get tx {}'.format(node, tx_hash))
    if result.__contains__("Error"):
        raise Exception('get tx failed!')
    tx = json.loads(result)
    if tx['height'] == 18446744073709551615:
        raise Exception('tx in pool!')
    return result


@retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
def get_abi(contract_addr):
    result = subprocess.getoutput(get_abi_fmt.format(contract_addr))
    if result.__contains__("Error"):
        raise Exception('get abi failed!')
    return result


@retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
def get_block(block):
    block_ret = subprocess.getoutput(get_block_fmt.format(block))
    if block_ret.__contains__("Error"):
        raise Exception("get block failed!")
    return block_ret


@retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
def get_system_config(node):
    result = subprocess.getoutput("cldi -c {} get system-config".format(node))
    if result.__contains__("Error"):
        raise Exception("get system-config failed!")
    return result


@retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
def exec_retry(cmd):
    result = subprocess.getoutput(cmd)
    if result.__contains__("Error"):
        raise Exception("exec failed: {}".format(cmd))
    return result


def exec(cmd):
    return subprocess.getoutput(cmd)


@retry(stop=stop_after_attempt(60), wait=wait_fixed(2), after=after_log(logger, logging.DEBUG))
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
        raise Exception("the job's status is still Active")
    return resource.get('status').get('status')


@retry(stop=stop_after_attempt(60), wait=wait_fixed(5), after=after_log(logger, logging.DEBUG))
def check_node_running(name, namespace):
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    node_sts = apps_v1.read_namespaced_stateful_set(name=name, namespace=namespace)
    if node_sts.status.ready_replicas != 1:
        raise Exception("chain node is not ready")


# wait for the block height to exceed the specified height
def wait_block_number_exceed_specified_height(specified_height, retry_times=DEFAULT_RETRY_TIMES, retry_wait=DEFAULT_RETRY_WAIT):
    @retry(stop=stop_after_attempt(retry_times), wait=wait_fixed(retry_wait), after=after_log(logger, logging.DEBUG))
    def inner_func():
        current_bn = get_block_number(retry_times=retry_times, retry_wait=retry_wait)
        if current_bn < specified_height:
            raise Exception("not exceed specified height")

    return inner_func()
