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

contract_code = "0x608060405234801561001057600080fd5b5060f58061001f6000396000f300608060405260" \
                "0436106053576000357c01000000000000000000000000000000000000000000000000000000" \
                "00900463ffffffff16806306661abd1460585780634f2be91f146080578063d826f88f146094" \
                "575b600080fd5b348015606357600080fd5b50606a60a8565b60405180828152602001915050" \
                "60405180910390f35b348015608b57600080fd5b50609260ae565b005b348015609f57600080" \
                "fd5b5060a660c0565b005b60005481565b60016000808282540192505081905550565b600080" \
                "819055505600a165627a7a72305820faa1d1f51d7b5ca2b200e0f6cdef4f2d7e44ee686209e300beb1146f40d32dee0029"

if __name__ == "__main__":
    create_result = util.exec_retry('cldi -c default rpc estimate-quota {}'.format(contract_code))
    create_quota = int(create_result)
    if create_quota > 0 :
        print("create contract estimate quota: {}".format(create_quota))
    else:
        exit(1)

    send_result = util.exec_retry('cldi -c default rpc estimate-quota -t 0xa4582f4966bdef3a2839e2f256a714426508ddb7 0x4f2be91f')
    send_quota = int(send_result)
    if send_quota > 0 :
        print("send transaction estimate quota: {}".format(send_quota))
    else:
        exit(1)
    exit(0)
