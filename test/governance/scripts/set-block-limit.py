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
import subprocess, json, time

import sys
sys.path.append("test/utils")
import util

DEFAULT_BLOCK_LIMIT = 100
NEW_BLOCK_LIMIT = 10
hex_prefix = '0x'


def is_json(res):
    try:
        json.loads(res)
    except ValueError:
        return False
    return True


def get_system_config():
    # get system-config
    result = subprocess.getoutput("cldi -c default get system-config")
    if not is_json(result):
        print("get system-config failed: {}", result)
        exit(10)
    return json.loads(result)


def set_block_limit(block_limit):
    set_cmd = "cldi -c default -u admin admin set-block-limit {}".format(block_limit)
    tx_hash = subprocess.getoutput(set_cmd)
    if not tx_hash.__contains__(hex_prefix) or not len(tx_hash) == len(hex_prefix) + 64:
        print("set-block-limit failed!")
        exit(20)
    util.get_tx(tx_hash)
    return tx_hash


if __name__ == "__main__":
    # get system-config
    block_limit = get_system_config()['block_limit']
    if not block_limit == DEFAULT_BLOCK_LIMIT:
        print("invalid block limit: ", block_limit)
        exit(30)

    # set block limit to 10
    tx_hash = set_block_limit(NEW_BLOCK_LIMIT)

    time.sleep(6)

    # check new block limit in system-config
    system_config = get_system_config()
    block_limit = system_config['block_limit']
    if not block_limit == NEW_BLOCK_LIMIT:
        print("block limit mismatch")
        exit(40)

    if system_config['block_limit_pre_hash'] != tx_hash:
        print("set-block-limit tx hash mismatch!")
        exit(50)

    # restore block limit
    tx_hash = set_block_limit(DEFAULT_BLOCK_LIMIT)

    time.sleep(6)

    # check new block limit in system-config
    system_config = get_system_config()
    block_limit = system_config['block_limit']
    if not block_limit == DEFAULT_BLOCK_LIMIT:
        print("block limit mismatch")
        exit(60)

    if system_config['block_limit_pre_hash'] != tx_hash:
        print("set-block-limit tx hash mismatch!")
        exit(70)

    exit(0)
