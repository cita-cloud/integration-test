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
import pprint
import sys
sys.path.append("test/utils")
import util

if __name__ == "__main__":
    good_flag = False
    bad_flag = False
    hex_prefix = '0x'
    good_addr = hex_prefix + ''.join(['0' for i in range(40)])
    bad_addr = hex_prefix + ''.join(['0' for j in range(39)])
    get_nonce_fmt = "cldi -c default get nonce {}"
    good_result = util.exec(get_nonce_fmt.format(good_addr))
    pprint.pprint("get nonce good_result: {good_result}".format(good_result=good_result), indent=4)
    bad_result = util.exec_bad(get_nonce_fmt.format(bad_addr))
    pprint.pprint("get nonce bad_result: {bad_result}".format(bad_result=bad_result), indent=4)
    if good_result.startswith(hex_prefix) \
            and len(good_result) == 64 + len(hex_prefix) and bad_result.__contains__('invalid hex input'):
        exit(0)
    exit(1)

