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
import sys
sys.path.append("test/utils")
import util

if __name__ == "__main__":
    hex_prefix = '0x'
    good_addr = hex_prefix + ''.join(['0' for i in range(40)])
    zero_balance = hex_prefix + ''.join(['0' for i in range(64)])
    result = util.exec_retry("cldi -c default get balance {}".format(good_addr))
    if result == zero_balance:
        exit(0)
    print("get balance error")
    exit(1)
