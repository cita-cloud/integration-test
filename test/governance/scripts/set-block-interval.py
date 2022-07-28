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
import subprocess, json, time, datetime

import sys
sys.path.append("test/utils")
import util

if __name__ == "__main__":
    # get system-config
    cmd = "cldi -c default get system-config"
    cmd_result = subprocess.getoutput(cmd)
    system_config = json.loads(cmd_result)
    old_block_interval = system_config['block_interval']
    if not old_block_interval == 3:
        print("invalid block interval: ", old_block_interval)
        exit(10)

    # set block interval to 10
    cmd = "cldi -c default -u admin admin set-block-interval 10"
    tx_hash = subprocess.getoutput(cmd)
    
    print("set-block-interval ret:", tx_hash)

    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("set-block-interval failed!")
        exit(20)

    time.sleep(10)

    util.get_tx(tx_hash)

    # check new block interval in system-config
    cmd = "cldi -c default get system-config"
    cmd_result = subprocess.getoutput(cmd)
    system_config = json.loads(cmd_result)

    if not system_config['block_interval'] == 10:
        print("block interval mismatch!", system_config)
        exit(40)

    if system_config['block_interval_pre_hash'] != tx_hash:
        print("set-block-interval tx hash mismatch!", system_config)
        exit(50)
    
    time.sleep(150)

    # check timestamp in block to verify block interval
    util.check_block_increase()

    result = util.get_block_number()

    latest_block_ret = util.get_block(result)

    pre_block_ret = util.get_block(result - 6)

    latest_block = json.loads(latest_block_ret)
    pre_block = json.loads(pre_block_ret)

    latest_block_time = datetime.datetime.strptime(latest_block['time'][:19], '%Y-%m-%d %H:%M:%S')
    pre_block_time = datetime.datetime.strptime(pre_block['time'][:19], '%Y-%m-%d %H:%M:%S')
    diff = latest_block_time - pre_block_time

    if diff.seconds / 6 < 5:
        print("block interval incoreect!", diff, pre_block_time, latest_block_time)
        exit(80)        

    # reset old block interval
    cmd = "cldi -c default -u admin admin set-block-interval 3"
    tx_hash = subprocess.getoutput(cmd)
    
    print("set-block-interval ret:", tx_hash)

    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("set-block-interval failed!")
        exit(90)
    
    time.sleep(30)

    util.get_tx(tx_hash)

    # check new block interval in system-config
    cmd = "cldi -c default get system-config"
    cmd_result = subprocess.getoutput(cmd)
    system_config = json.loads(cmd_result)

    if not system_config['block_interval'] == 3:
        print("block interval mismatch!", system_config)
        exit(110)

    if system_config['block_interval_pre_hash'] != tx_hash:
        print("set-block-interval tx hash mismatch!", system_config)
        exit(120)

    time.sleep(100)

    # check timestamp in block to verify block interval
    util.check_block_increase()

    result = util.get_block_number()

    latest_block_ret = util.get_block(result)

    pre_block_ret = util.get_block(result - 6)

    latest_block = json.loads(latest_block_ret)
    pre_block = json.loads(pre_block_ret)

    latest_block_time = datetime.datetime.strptime(latest_block['time'][:19], '%Y-%m-%d %H:%M:%S')
    pre_block_time = datetime.datetime.strptime(pre_block['time'][:19], '%Y-%m-%d %H:%M:%S')
    diff = latest_block_time - pre_block_time

    if diff.seconds / 6 > 5:
        print("block interval incoreect!", diff, pre_block_time, latest_block_time)
        exit(150)

    exit(0)
