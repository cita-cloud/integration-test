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

import sys
sys.path.append("test/utils")
import util


def check(result):
    try:
        json_obj = json.loads(result)
    except ValueError:
        if not result.__contains__(' message: "NoTransaction"') and not result.__contains__(' message: "NoTxHeight"'):
            exit(10)
        return
    if isinstance(json_obj['height'], int) and isinstance(json_obj['index'], int):
        exit(0)
    exit(20)


if __name__ == "__main__":
    send_result = util.exec_retry("cldi -c default send {} 0x".format('0x' + ''.join(['0' for i in range(40)])))
    result = util.get_tx(send_result)
    check(result)
