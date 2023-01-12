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

if __name__ == "__main__":
    result = util.exec_retry("cldi -c default get node-status")
    pprint.pprint("get node-status: {result}".format(result=result), indent=4)
    try:
        json_obj = json.loads(result)
        is_sync = json_obj['is_sync']
        peers_count = json_obj['peers_count']
        peers_status = json_obj['peers_status']
        version = json_obj['version']
        if isinstance(is_sync, bool) and isinstance(peers_status, list) and isinstance(peers_count, int) and isinstance(version, str):
            exit(0)
    except ValueError:
        pass
    exit(1)
