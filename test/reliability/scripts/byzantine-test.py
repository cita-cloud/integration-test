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


import subprocess, time

import sys
import os
sys.path.append("test/utils")
import util

if __name__ == "__main__":
    # raft chain don't need to execute this test
    if os.getenv("CHAIN_TYPE") == "tls-raft":
        print("raft chain don't need to execute byzantine test")
        exit(0)

    # now we have 4 node
    cmd = "kubectl get pod -ncita --no-headers=true -l app.kubernetes.io/chain-name=$CHAIN_NAME | wc -l"
    node_count = int(subprocess.getoutput(cmd))
    if node_count != 4:
        print("There are no 4 node, can't fault tolerance!", node_count)
        exit(10)
    
    # check work well
    util.check_block_increase()
    
    # for BFT we can Fault Tolerance 1
    # shutdown 1 node is ok
    cmd = "kubectl get sts -ncita --no-headers=true -l app.kubernetes.io/chain-name=$CHAIN_NAME | tail -n 1 | awk '{print $1}'"
    node3_name = subprocess.getoutput(cmd)
    cmd = "kubectl scale sts {} --replicas=0 -ncita"
    ret = subprocess.getoutput(cmd.format(node3_name))
    if not ret.__contains__("scaled"):
        print("stop node failed!", ret)
        exit(30)

    time.sleep(60)
    
    # check work well
    util.check_block_increase()

    # shutdown 2 node is not ok
    cmd = "kubectl get sts -ncita --no-headers=true -l app.kubernetes.io/chain-name=$CHAIN_NAME | tail -n 2 | head -n 1 | awk '{print $1}'"
    node2_name = subprocess.getoutput(cmd)
    cmd = "kubectl scale sts {} --replicas=0 -ncita"
    ret = subprocess.getoutput(cmd.format(node2_name))
    if not ret.__contains__("scaled"):
        print("stop node failed!", ret)
        exit(50)

    time.sleep(60)
    
    # check work not well
    pre_block_numbner = util.get_block_number()

    time.sleep(30)

    latest_block_numbner = util.get_block_number()

    if latest_block_numbner > pre_block_numbner:
        print("block number should not increase!", pre_block_numbner, latest_block_numbner)
        exit(60)

    # restore 2 node, chain will be ok
    cmd = "kubectl scale sts {} --replicas=1 -ncita"
    ret = subprocess.getoutput(cmd.format(node3_name))
    if not ret.__contains__("scaled"):
        print("start node failed!", ret)
        exit(70)
    
    ret = subprocess.getoutput(cmd.format(node2_name))
    if not ret.__contains__("scaled"):
        print("start node failed!", ret)
        exit(71)

    for i in range(5):
        time.sleep(60)
        cmd = "kubectl get pod -ncita --no-headers=true -l app.kubernetes.io/chain-name=$CHAIN_NAME | grep {} | grep Running"
        ret2 = subprocess.getoutput(cmd.format(node2_name))
        ret3 = subprocess.getoutput(cmd.format(node3_name))
        if len(ret2) != 0 and len(ret3) != 0:
            break
        if i == 4:
            print("restore node failed!")
            exit(75)
    
    # check work well
    util.check_block_increase()

    exit(0)
