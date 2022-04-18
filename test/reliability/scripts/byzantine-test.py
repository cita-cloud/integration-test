#!/usr/bin/python
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


import subprocess, sys, json, time

if __name__ == "__main__":
    # now we have 4 node
    cmd = "kubectl get pod -ncita | grep my-chain | wc -l"
    node_count = int(subprocess.getoutput(cmd))
    if node_count != 4:
        print("There are no 4 node, can't fault tolerance!")
        exit(10)
    
    # check work well
    pre_block_numbner = int(subprocess.getoutput("cldi -c default get block-number"))

    time.sleep(6)

    latest_block_numbner = int(subprocess.getoutput("cldi -c default get block-number"))

    if not latest_block_numbner > pre_block_numbner:
        print("block number not increase!")
        exit(20)
    
    # for BFT we can Fault Tolerance 1
    # shutdown 1 node is ok
    cmd = "kubectl get svc -ncita --no-headers=true -l app.kubernetes.io/chain-name=my-chain | tail -n 1 | awk '{print $1}'"
    node3_name = subprocess.getoutput(cmd)[:21]
    cmd = "cco-cli node stop {}"
    ret = subprocess.getoutput(cmd.format(node3_name))
    if not ret.__contains__("success"):
        print("stop node failed!")
        exit(30)

    time.sleep(60)
    
    # check work well
    pre_block_numbner = int(subprocess.getoutput("cldi -c default get block-number"))

    time.sleep(6)

    latest_block_numbner = int(subprocess.getoutput("cldi -c default get block-number"))

    if not latest_block_numbner > pre_block_numbner:
        print("block number not increase!")
        exit(40)

    # shutdown 2 node is not ok
    cmd = "kubectl get svc -ncita --no-headers=true -l app.kubernetes.io/chain-name=my-chain | tail -n 2 | awk '{print $1}'"
    node2_name = subprocess.getoutput(cmd)[:21]
    cmd = "cco-cli node stop {}"
    ret = subprocess.getoutput(cmd.format(node2_name))
    if not ret.__contains__("success"):
        print("stop node failed!")
        exit(50)

    time.sleep(60)
    
    # check work well
    pre_block_numbner = int(subprocess.getoutput("cldi -c default get block-number"))

    time.sleep(6)

    latest_block_numbner = int(subprocess.getoutput("cldi -c default get block-number"))

    if latest_block_numbner > pre_block_numbner:
        print("block number should not increase!")
        exit(60)
    

    # restore 2 node, chain will be ok
    cmd = "cco-cli node start {}"
    ret = subprocess.getoutput(cmd.format(node3_name))
    if not ret.__contains__("success"):
        print("start node failed!")
        exit(70)
    
    ret = subprocess.getoutput(cmd.format(node2_name))
    if not ret.__contains__("success"):
        print("start node failed!")
        exit(70)

    time.sleep(90)
    
    # check work well
    pre_block_numbner = int(subprocess.getoutput("cldi -c default get block-number"))

    time.sleep(6)

    latest_block_numbner = int(subprocess.getoutput("cldi -c default get block-number"))

    if not latest_block_numbner > pre_block_numbner:
        print("block number not increase!")
        exit(80)

    exit(0)
