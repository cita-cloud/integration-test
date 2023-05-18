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
import os
import sys
sys.path.append("test/utils")
import util

if __name__ == "__main__":
    # raft chain don't need to execute this test
    if os.getenv("CHAIN_TYPE") == "zenoh-raft":
        print("raft proof is empty, skip parse-proof test")
        exit(0)

    result = util.exec_retry("cldi -c default get block 1")
    try:
        json_obj = json.loads(result)
        proof = json_obj['proof']
        result = util.exec_retry("cldi -c default rpc parse-proof {}".format(proof))
        json_obj1 = json.loads(result)
        height = json_obj1['height']
        signature = json_obj1['signature']
        validators = json_obj1['validators']
        if isinstance(height, int) and isinstance(signature, str) and isinstance(validators, list):
            exit(0)
    except ValueError:
        pass
    exit(1)
