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
import subprocess, sys, json

if __name__ == "__main__":
    good_height = 1
    bad_height = sys.maxsize
    bad_hash = '0x' + ''.join(['0' for i in range(64)])
    cmd = "cldi -c default get block {}"
    height_good_result = subprocess.getoutput(cmd.format(1))
    height_bad_result = subprocess.getoutput(cmd.format(sys.maxsize))
    try:
        result = json.loads(height_good_result)
        if result['height'] != good_height:
            exit(10)
    except ValueError:
        exit(20)
    if not height_bad_result.__contains__(' message: "NoBlock"'):
        exit(30)

    good_hash = subprocess.getoutput("cldi -c default get block-hash {}".format(good_height))
    hash_good_result = subprocess.getoutput(cmd.format(good_hash))
    hash_bad_result = subprocess.getoutput(cmd.format(bad_hash))

    try:
        result = json.loads(hash_good_result)
        if result['height'] != good_height:
            exit(40)
    except ValueError:
        exit(50)
    if not hash_bad_result.__contains__(' message: "NoBlockHeight"'):
        exit(60)
    exit(0)


