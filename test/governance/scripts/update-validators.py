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
sys.path.append("../../utils")
import util

if __name__ == "__main__":
    # get system-config
    cmd = "cldi -c default get system-config"
    cmd_result = subprocess.getoutput(cmd)
    system_config = json.loads(cmd_result)

    # get current validator list
    validators = system_config['validators']
    validators_arg = ""
    for validator in validators:
        validators_arg += validator
        validators_arg += " "
    print("validators_arg: ", validators_arg)

    # fake validator
    fake_validator = "0x545055b46b8292a82ba6e2d6e51014df1a2ac230"

    # append validator
    cmd = "cldi -c default -u admin admin update-validators {}"
    tx_hash = subprocess.getoutput(cmd.format(validators_arg + fake_validator))
    
    print("update-validators ret:", tx_hash)

    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("update-validators failed!")
        exit(10)

    util.get_tx(tx_hash)

    # check new validators in system-config
    cmd = "cldi -c default get system-config"
    cmd_result = subprocess.getoutput(cmd)
    system_config = json.loads(cmd_result)

    if not system_config['validators'].__contains__(fake_validator):
        print("validators mismatch!", system_config)
        exit(30)

    if system_config['validators_pre_hash'] != tx_hash:
        print("update-validators tx hash mismatch!", system_config)
        exit(40)


    # reset old validators
    cmd = "cldi -c default -u admin admin update-validators {}"
    tx_hash = subprocess.getoutput(cmd.format(validators_arg))
    
    print("update-validators ret:", tx_hash)

    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("update-validators failed!")
        exit(50)

    util.get_tx(tx_hash)

    # check new validators in system-config
    cmd = "cldi -c default get system-config"
    cmd_result = subprocess.getoutput(cmd)
    system_config = json.loads(cmd_result)

    if system_config['validators'].__contains__(fake_validator):
        print("validators mismatch!", system_config)
        exit(70)

    if system_config['validators_pre_hash'] != tx_hash:
        print("update-validators tx hash mismatch!", system_config)
        exit(80)

    exit(0)
