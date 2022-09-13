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

from tenacity import retry,stop_after_attempt,wait_fixed,after_log
import logging
import subprocess
import time
import sys
import json

logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)
logger = logging.getLogger(__name__)

retry_times = 5
retry_wait = 10

get_receipt_fmt = 'cldi -c default get receipt {}'
get_abi_fmt = 'cldi -c default get abi {}'
get_tx_fmt = 'cldi -c default get tx {}'
get_block_fmt = "cldi -c default get block {}"

@retry(stop=stop_after_attempt(retry_times),wait=wait_fixed(retry_wait),after=after_log(logger,logging.DEBUG))
def get_block_number():
    return int(subprocess.getoutput("cldi -c default get block-number"))


@retry(stop=stop_after_attempt(retry_times),wait=wait_fixed(retry_wait),after=after_log(logger,logging.DEBUG))
def check_block_increase():
    old = get_block_number()
    time.sleep(30)
    new = get_block_number()
    if new == old:
        raise Exception('block not increase!')


@retry(stop=stop_after_attempt(retry_times),wait=wait_fixed(retry_wait),after=after_log(logger,logging.DEBUG))
def get_node_block_number(node):
    get_node_block_fmt = 'cldi -c {} get block-number'
    return int(subprocess.getoutput(get_node_block_fmt.format(node)))

        
@retry(stop=stop_after_attempt(retry_times),wait=wait_fixed(retry_wait),after=after_log(logger,logging.DEBUG))
def check_node_block_increase(node):
    old = get_node_block_number(node)
    time.sleep(30)
    new = get_node_block_number(node)
    if new == old:
        raise Exception('{} block not increase!'.format(node))


@retry(stop=stop_after_attempt(retry_times),wait=wait_fixed(retry_wait),after=after_log(logger,logging.DEBUG))
def get_receipt(tx_hash):
    result = subprocess.getoutput(get_receipt_fmt.format(tx_hash))
    if result.__contains__("Error"):
        raise Exception('get receipt failed!')
    return result


@retry(stop=stop_after_attempt(retry_times),wait=wait_fixed(retry_wait),after=after_log(logger,logging.DEBUG))
def get_tx(tx_hash):
    result = subprocess.getoutput(get_tx_fmt.format(tx_hash))
    if result.__contains__("Error"):
        raise Exception('get tx failed!')
    tx = json.loads(result)
    if tx['height'] == 18446744073709551615:
        raise Exception('tx in pool!')
    return result


@retry(stop=stop_after_attempt(retry_times),wait=wait_fixed(retry_wait),after=after_log(logger,logging.DEBUG))
def get_abi(contract_addr):
    result = subprocess.getoutput(get_abi_fmt.format(contract_addr))
    if result.__contains__("Error"):
        raise Exception('get abi failed!')
    return result


@retry(stop=stop_after_attempt(retry_times),wait=wait_fixed(retry_wait),after=after_log(logger,logging.DEBUG))
def get_block(block):
    block_ret = subprocess.getoutput(get_block_fmt.format(block))
    if block_ret.__contains__("Error"):
        raise Exception("get block failed!")
    return block_ret


@retry(stop=stop_after_attempt(retry_times),wait=wait_fixed(retry_wait),after=after_log(logger,logging.DEBUG))
def get_system_config(node):
    result = subprocess.getoutput("cldi -c {} get system-config".format(node))
    if result.__contains__("Error"):
        raise Exception("get system-config failed!")
    return result


@retry(stop=stop_after_attempt(retry_times),wait=wait_fixed(retry_wait),after=after_log(logger,logging.DEBUG))
def exec(cmd):
    result = subprocess.getoutput(cmd)
    if result.__contains__("Error"):
        raise Exception("exec failed: {}".format(cmd))
    return result
