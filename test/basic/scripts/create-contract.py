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

# creat contract get receipt get code
import json
import pprint
import sys
sys.path.append("test/utils")
import util

no_receipt_message = ' message: "Not get the receipt"'
hex_prefix = '0x'

bad_hash = hex_prefix + ''.join(['0' for i in range(64)])
bad_contract_addr = hex_prefix + ''.join(['0' for j in range(40)])

contract_code = "0x608060405234801561001057600080fd5b5060f58061001f6000396000f300608060405260" \
                "0436106053576000357c01000000000000000000000000000000000000000000000000000000" \
                "00900463ffffffff16806306661abd1460585780634f2be91f146080578063d826f88f146094" \
                "575b600080fd5b348015606357600080fd5b50606a60a8565b60405180828152602001915050" \
                "60405180910390f35b348015608b57600080fd5b50609260ae565b005b348015609f57600080" \
                "fd5b5060a660c0565b005b60005481565b60016000808282540192505081905550565b600080" \
                "819055505600a165627a7a72305820faa1d1f51d7b5ca2b200e0f6cdef4f2d7e44ee686209e300beb1146f40d32dee0029"

create_fmt = 'cldi -c default create {}'
get_receipt_fmt = 'cldi -c default get receipt {}'
get_code_fmt = 'cldi -c default get code {}'
get_abi_fmt = 'cldi -c default get abi {}'
store_abi_fmt = 'cldi -c default rpc store-abi {} {}'

abi = '[]'

if __name__ == "__main__":
    util.check_block_increase()

    create_result = util.exec_retry(create_fmt.format(contract_code))
    pprint.pprint("create_result: {create_result}".format(create_result=create_result))
    if not create_result.startswith(hex_prefix) or not len(create_result) == 2 + 64:
        exit(10)
    bad_receipt = util.exec(get_receipt_fmt.format(bad_hash))
    if not bad_receipt.__contains__(no_receipt_message):
        pprint.pprint("bad_receipt: {bad_receipt}".format(bad_receipt=bad_receipt))
        exit(20)

    if hex_prefix != util.exec_retry(get_code_fmt.format(bad_contract_addr)):
        exit(30)

    result = util.get_receipt(create_result)

    json_obj = json.loads(result)
    contract_addr = json_obj['contract_addr']

    code = util.exec_retry(get_code_fmt.format(contract_addr))
    if not code.startswith(hex_prefix):
        exit(32)

    if util.exec(get_abi_fmt.format(bad_contract_addr)) != '':
        exit(34)
    
    store_abi_result = util.exec_retry(store_abi_fmt.format(contract_addr, abi))
    pprint.pprint("store_abi_result: {store_abi_result}".format(store_abi_result=store_abi_result))
    if not store_abi_result.startswith(hex_prefix):
        exit(33)

    util.get_receipt(store_abi_result)

    result = util.get_abi(contract_addr)    
    if  result!= abi:
        pprint.pprint("abi not correct!: {result}".format(result=result))
        exit(35)
    
    exit(0)
