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
import subprocess

if __name__ == "__main__":

    result = subprocess.getoutput("cldi get peers-info")
    try:
        json_obj = json.loads(result)
        node_list = json_obj['nodes']
        if isinstance(node_list, list):
            if len(node_list) == 0:
                exit(0)
            else:
                node_0 = node_list[0]
                if len(node_0) == 4 and isinstance(node_0['address'], str) and isinstance(node_0['host'], str) \
                        and isinstance(node_0['origin'], int) and isinstance(node_0['port'], int):
                    exit(0)
    except ValueError:
        pass
    exit(1)