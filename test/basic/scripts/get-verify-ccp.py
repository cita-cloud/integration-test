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
import os

hex_prefix = '0x'

contract_code = "0x608060405234801561001057600080fd5b5060f58061001f6000396000f300608060405260" \
                "0436106053576000357c01000000000000000000000000000000000000000000000000000000" \
                "00900463ffffffff16806306661abd1460585780634f2be91f146080578063d826f88f146094" \
                "575b600080fd5b348015606357600080fd5b50606a60a8565b60405180828152602001915050" \
                "60405180910390f35b348015608b57600080fd5b50609260ae565b005b348015609f57600080" \
                "fd5b5060a660c0565b005b60005481565b60016000808282540192505081905550565b600080" \
                "819055505600a165627a7a72305820faa1d1f51d7b5ca2b200e0f6cdef4f2d7e44ee686209e300beb1146f40d32dee0029"

create_fmt = 'cldi -c default create {}'

if __name__ == "__main__":
    # send tx
    util.check_block_increase()

    create_result = util.exec_retry(create_fmt.format(contract_code))
    pprint.pprint("create_result: {create_result}".format(create_result=create_result))
    if not create_result.startswith(hex_prefix) or not len(create_result) == 2 + 64:
        exit(10)

    result = util.get_receipt(create_result)

    json_obj = json.loads(result)
    height = json_obj['block_number']

    ccp = util.get_cross_chain_proof(create_result)

    ccp_file = "{}-ccp".format(create_result[2:18])
    verify_result = util.verify_cross_chain_proof(ccp_file)
    pprint.pprint("verify_cross_chain_proof: {verify_result}".format(verify_result=verify_result))
    json_result = json.loads(verify_result)

    if os.getenv("CHAIN_TYPE") == "raft":
        if not json_result['code'] == 4:
            exit(40)
    else:
        if not json_result['code'] == 0:
            exit(20)

    if os.path.exists(ccp_file):
        os.remove(ccp_file)

    # do nothing
    receipt_proof = util.get_receipt_proof(create_result)
    pprint.pprint("get_receipt_proof: {receipt_proof}".format(receipt_proof=receipt_proof))

    roots_info = util.get_roots_info(height)
    json_roots_info = json.loads(roots_info)
    if json_roots_info['height'] != height:
        exit(30)

    exit(0)
