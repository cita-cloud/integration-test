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
import subprocess, json, os

import sys, time
sys.path.append("test/utils")
import util
import yaml

if __name__ == "__main__":
    # get system-config
    cmd = "cldi -c node4 get system-config"
    cmd_result = subprocess.getoutput(cmd)
    system_config = json.loads(cmd_result)

    # get current validator list
    validators = system_config['validators']
    validators_arg = ""
    for validator in validators:
        validators_arg += validator
        validators_arg += " "
    print("validators_arg: ", validators_arg)

    # add sync node address
    sync_node_account_path = "test/operations/resource/" + os.getenv("CHAIN_TYPE") + "/" + os.getenv("CHAIN_NAME") + "-node4/cm-account.yaml"
    with open(sync_node_account_path, "r") as sync_node_config:
        temp = yaml.load(sync_node_config.read())
        sync_node_addr = temp['data']['node_address']
        validators_arg += sync_node_addr
    

    # update validators
    cmd = "cldi -c node4 -u admin admin update-validators {}"
    tx_hash = subprocess.getoutput(cmd.format(validators_arg))
    
    print("update-validators ret:", tx_hash)

    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("update-validators failed!")
        exit(50)

    util.get_tx(tx_hash)

    # check new validators in system-config
    cmd = "cldi -c node4 get system-config"
    cmd_result = subprocess.getoutput(cmd)
    system_config = json.loads(cmd_result)

    if not system_config['validators'].__contains__(sync_node_addr):
        print("validators mismatch!", system_config)
        exit(70)

    if system_config['validators_pre_hash'] != tx_hash:
        print("update-validators tx hash mismatch!", system_config)
        exit(80)

    old = int(subprocess.getoutput("cldi -c node4 get block-number"))
    time.sleep(30)
    new = int(subprocess.getoutput("cldi -c node4 get block-number"))
    if new == old:
        print("sync validator node4 not increase!")
        exit(90)

    exit(0)
