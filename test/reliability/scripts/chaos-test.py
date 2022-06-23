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
import os
import subprocess
import time

import sys
sys.path.append("test/utils")
import util

apply_cmd = "kubectl apply -f {}"
delete_cmd = "kubectl delete -f {}"


def clean(chain_type):
    subprocess.getoutput(delete_cmd.format("test/reliability/chaos/network-chaos.yaml"))
    subprocess.getoutput(delete_cmd.format("test/reliability/chaos/pod-chaos.yaml"))
    subprocess.getoutput(delete_cmd.format("test/reliability/chaos/io-chaos.yaml"))


def exec_chaos():
    # network chaos test 240s
    ret = subprocess.getoutput(apply_cmd.format("test/reliability/chaos/network-chaos.yaml"))
    if not ret.__contains__("created"):
        print("apply network chaos test failed!", ret)
        clean()
        exit(10)

    time.sleep(300)

    # delete network chaos test
    ret = subprocess.getoutput(delete_cmd.format("test/reliability/chaos/network-chaos.yaml"))
    if not ret.__contains__("deleted"):
        print("delete network chaos test failed!", ret)
        exit(20)

        # check work well
    util.check_block_increase()

    # pod chaos test 400s
    ret = subprocess.getoutput(apply_cmd.format("test/reliability/chaos/pod-chaos.yaml"))
    if not ret.__contains__("created"):
        print("apply pod chaos test failed!", ret)
        clean()
        exit(40)

    time.sleep(600)

    # delete pod chaos test
    ret = subprocess.getoutput(delete_cmd.format("test/reliability/chaos/pod-chaos.yaml"))
    if not ret.__contains__("deleted"):
        print("delete pod chaos test failed!", ret)
        exit(50)

    # check work well
    util.check_block_increase()

    # io chaos test 300s
    ret = subprocess.getoutput(apply_cmd.format("test/reliability/chaos/io-chaos.yaml"))
    if not ret.__contains__("created"):
        print("apply io chaos test failed!", ret)
        clean()
        exit(70)

    time.sleep(400)

    # delete io chaos test
    ret = subprocess.getoutput(delete_cmd.format("test/reliability/chaos/io-chaos.yaml"))
    if not ret.__contains__("deleted"):
        print("delete io chaos test failed!", ret)
        exit(80)

    # check work well
    util.check_block_increase()

    exit(0)


if __name__ == "__main__":
    print("start exec chaos test for {}".format(os.getenv("CHAIN_NAME")))
    subprocess.getoutput("sed -i 's/XXXXXX/{}/g'".format(os.getenv("CHAIN_NAME")))
    exec_chaos()
