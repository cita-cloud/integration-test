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


def is_json(res):
    try:
        json.loads(res)
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    result = util.exec_retry("cldi -c default get system-config")
    pprint.pprint("get system-config: {result}".format(result=result), indent=4)
    if is_json(result):
        exit(0)
    exit(1)
