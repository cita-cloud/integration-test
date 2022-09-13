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
import json
import pprint
import sys
sys.path.append("test/utils")
import util

if __name__ == "__main__":
    good_height = 1
    bad_height = sys.maxsize
    bad_hash = '0x' + ''.join(['0' for i in range(64)])
    cmd = "cldi -c default get block {}"
    height_good_result = util.exec_retry(cmd.format(1))
    pprint.pprint("height_good_result: {height_good_result}".format(height_good_result=height_good_result))
    height_bad_result = util.exec(cmd.format(sys.maxsize))
    pprint.pprint("height_bad_result: {height_bad_result}".format(height_bad_result=height_bad_result))
    try:
        result = json.loads(height_good_result)
        if result['height'] != good_height:
            exit(10)
    except ValueError:
        exit(20)
    if not height_bad_result.__contains__("Error: current_height:"):
        exit(30)

    good_hash = util.exec_retry("cldi -c default get block-hash {}".format(good_height))
    pprint.pprint("good_hash: {good_hash}".format(good_hash=good_hash))
    hash_good_result = util.exec_retry(cmd.format(good_hash))
    pprint.pprint("hash_good_result: {hash_good_result}".format(hash_good_result=hash_good_result))
    hash_bad_result = util.exec(cmd.format(bad_hash))
    pprint.pprint("hash_bad_result: {hash_bad_result}".format(hash_bad_result=hash_bad_result))

    try:
        result = json.loads(hash_good_result)
        if result['height'] != good_height:
            exit(40)
    except ValueError:
        exit(50)
    if not hash_bad_result.__contains__(' message: "NoBlockHeight"'):
        exit(60)
    exit(0)
