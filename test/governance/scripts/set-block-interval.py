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
import subprocess, sys, json, time, datetime

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

    time.sleep(6)

    cmd = "cldi -c default get tx {}"
    cmd_result = subprocess.getoutput(cmd.format(tx_hash))
    if cmd_result.__contains__("Error"):
        print("get set-block-interval tx failed")
        exit(30)

    # check new block interval in system-config
    cmd = "cldi -c default get system-config"
    cmd_result = subprocess.getoutput(cmd)
    system_config = json.loads(cmd_result)

    if not system_config['block_interval'] == 10:
        print("block interval mismatch")
        exit(40)

    if system_config['block_interval_pre_hash'] != tx_hash:
        print("set-block-interval tx hash mismatch!")
        exit(50)

    # check timestamp in block to verify block interval
    time.sleep(30)
    result = int(subprocess.getoutput("cldi -c default get block-number"))
    cmd = "cldi -c default get block {}"
    latest_block_ret = subprocess.getoutput(cmd.format(result))
    if latest_block_ret.__contains__("Error"):
        print("get block failed!")
        exit(60)

    pre_block_ret = subprocess.getoutput(cmd.format(result - 1))
    if pre_block_ret.__contains__("Error"):
        print("get block failed!")
        exit(70)

    latest_block = json.loads(latest_block_ret)
    pre_block = json.loads(pre_block_ret)

    latest_block_time = datetime.datetime.strptime(latest_block['timestamp'][:19], '%Y-%m-%d %H:%M:%S')
    pre_block_time = datetime.datetime.strptime(pre_block['timestamp'][:19], '%Y-%m-%d %H:%M:%S')
    diff = latest_block_time - pre_block_time

    if diff.seconds < 8:
        print("block interval incoreect: ", diff)
        exit(80)        

    # reset old block interval
    cmd = "cldi -c default -u admin admin set-block-interval 3"
    tx_hash = subprocess.getoutput(cmd)
    
    print("set-block-interval ret:", tx_hash)

    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("set-block-interval failed!")
        exit(90)

    time.sleep(30)

    cmd = "cldi -c default get tx {}"
    cmd_result = subprocess.getoutput(cmd.format(tx_hash))
    if cmd_result.__contains__("Error"):
        print("get set-block-interval tx failed")
        exit(100)

    # check new block interval in system-config
    cmd = "cldi -c default get system-config"
    cmd_result = subprocess.getoutput(cmd)
    system_config = json.loads(cmd_result)

    if not system_config['block_interval'] == 3:
        print("block interval mismatch")
        exit(110)

    if system_config['block_interval_pre_hash'] != tx_hash:
        print("set-block-interval tx hash mismatch!")
        exit(120)

    # check timestamp in block to verify block interval
    time.sleep(9)
    result = int(subprocess.getoutput("cldi -c default get block-number"))
    cmd = "cldi -c default get block {}"
    latest_block_ret = subprocess.getoutput(cmd.format(result))
    if latest_block_ret.__contains__("Error"):
        print("get block failed!")
        exit(130)

    pre_block_ret = subprocess.getoutput(cmd.format(result - 1))
    if pre_block_ret.__contains__("Error"):
        print("get block failed!")
        exit(140)

    latest_block = json.loads(latest_block_ret)
    pre_block = json.loads(pre_block_ret)

    latest_block_time = datetime.datetime.strptime(latest_block['timestamp'][:19], '%Y-%m-%d %H:%M:%S')
    pre_block_time = datetime.datetime.strptime(pre_block['timestamp'][:19], '%Y-%m-%d %H:%M:%S')
    diff = latest_block_time - pre_block_time

    if diff.seconds > 5:
        print("block interval incoreect: ", diff)
        exit(150)        

    exit(0)
