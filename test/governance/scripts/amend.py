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

'''
// add contract
pragma solidity ^0.4.24;

/// @title An example contract to test batch tx
/// @author ["Rivtower Technologies <contact@rivtower.com>"]
contract SelfAdd {
    uint public x;

    event OneAdded(uint indexed x);

    /// @notice Add one every be called
    function AddOne() public {
        x += 1;
        emit OneAdded(x);
    }
}
'''
add_contract_code = "0x608060405234801561001057600080fd5b5060fd8061001f6000396000f3006080604052600436106049576000357c" \
                    "0100000000000000000000000000000000000000000000000000000000900463ffffffff1680630c55699c14604e5780" \
                    "632d910f2c146076575b600080fd5b348015605957600080fd5b506060608a565b604051808281526020019150506040" \
                    "5180910390f35b348015608157600080fd5b5060886090565b005b60005481565b600160008082825401925050819055" \
                    "506000547f11c1a8e7158fead62641b1e07f61c32daccb5a0432cabfe33a43e8de610042f160405160405180910390a2" \
                    "5600a165627a7a723058202803c9f7d2d620651f4a1e300c729d6e6f7ac45cd30ec60397d91d5c3e5773780029"
add_contract_abi = 'hello'

'''
// add contract
pragma solidity ^0.4.24;

/// @title An example contract to test batch tx
/// @author ["Rivtower Technologies <contact@rivtower.com>"]
contract SelfAdd {
    uint public x;

    event OneAdded(uint indexed x);

    /// @notice Add one every be called
    function AddOne() public {
        x += 1;
        emit OneAdded(x);
    }

    /// @notice Delete one each call
    function DeleteOne() public {
        x -= 1;
    }
}
'''
'''
// function hash
{
    "2d910f2c": "AddOne()",
    "6a033dc6": "DeleteOne()",
    "0c55699c": "x()"
}
'''
amend_contract_code = "0x608060405260043610610057576000357c0100000000000000000000000000000000000000000000000000000000" \
                      "900463ffffffff1680630c55699c1461005c5780632d910f2c146100875780636a033dc61461009e575b600080fd5b" \
                      "34801561006857600080fd5b506100716100b5565b6040518082815260200191505060405180910390f35b34801561" \
                      "009357600080fd5b5061009c6100bb565b005b3480156100aa57600080fd5b506100b36100fc565b005b6000548156" \
                      "5b600160008082825401925050819055506000547f11c1a8e7158fead62641b1e07f61c32daccb5a0432cabfe33a43" \
                      "e8de610042f160405160405180910390a2565b600160008082825403925050819055505600a165627a7a723058201a" \
                      "29baf45e5f8786c2042d57f00cb3865f5911d6694b116e099f6725018d0c3f0029"
amend_contract_abi = 'world'

create_fmt = 'cldi -c default create {}'
send_fmt = 'cldi -c default send {} {}'
call_fmt = 'cldi -c default call {} {}'
amend_code = 'cldi -c default -u admin admin amend code {} {}'
get_code = 'cldi -c default get code {}'
amend_abi = 'cldi -c default -u admin admin amend abi {} {}'
get_abi = 'cldi -c default get abi {}'
store_abi = 'cldi -c default rpc store-abi {} {}'
amend_kv = 'cldi -c default -u admin admin amend set-h256 {} {} {}'
get_kv = 'cldi -c default get storage-at {} {}'
amend_balance = 'cldi -c default -u admin admin amend balance {} {}'
get_balance = 'cldi -c default get balance {}'
hex_prefix = '0x'

amend_account = '0x37e30b0b304511adc34c512d47a83188d42cf575'
key_position = '0x0000000000000000000000000000000000000000000000000000000000000000'
add_result = '0x0000000000000000000000000000000000000000000000000000000000000001'
amend_num = '0x000000000000000000000000000000000000000000000000000000000000000a'

if __name__ == "__main__":
    util.check_block_increase()

    create_result = util.exec_retry(create_fmt.format(add_contract_code))
    pprint.pprint("create_result: {create_result}".format(create_result=create_result))
    if not create_result.startswith(hex_prefix) or not len(create_result) == 2 + 64:
        exit(10)

    result = util.get_receipt(create_result)

    json_obj = json.loads(result)
    contract_addr = json_obj['contract_addr']

    # invoke contract
    invoke_result = util.exec_retry(send_fmt.format(contract_addr, '0x2d910f2c'))
    if not invoke_result.startswith(hex_prefix) or not len(invoke_result) == 2 + 64:
        exit(20)

    result = util.get_receipt(invoke_result)
    call_result = util.exec_retry(call_fmt.format(contract_addr, '0x0c55699c'))
    if not call_result == add_result:
        exit(30)

    # store abi
    store_result = util.exec_retry(store_abi.format(contract_addr, add_contract_abi))
    if not store_result.startswith(hex_prefix) or not len(store_result) == 2 + 64:
        exit(40)
    result = util.get_receipt(store_result)

    abi_ressult = util.exec_retry(get_abi.format(contract_addr))
    if not abi_ressult == add_contract_abi:
        exit(50)

    # get kv
    get_kv_result = util.exec_retry(get_kv.format(contract_addr, key_position))
    if not get_kv_result == add_result:
        exit(60)

    # amend code
    amend_code_result = util.exec_retry(amend_code.format(contract_addr, amend_contract_code))
    if not amend_code_result.startswith(hex_prefix) or not len(amend_code_result) == 2 + 64:
        exit(70)

    result = util.get_receipt(amend_code_result)
    get_code_result = util.exec_retry(get_code.format(contract_addr))
    if not get_code_result == amend_contract_code:
        exit(80)

    # invoke new function
    invoke_result2 = util.exec_retry(send_fmt.format(contract_addr, '0x6a033dc6'))
    if not invoke_result2.startswith(hex_prefix) or not len(invoke_result2) == 2 + 64:
        exit(90)

    result = util.get_receipt(invoke_result2)
    call_result2 = util.exec_retry(call_fmt.format(contract_addr, '0x0c55699c'))
    if not call_result2 == key_position:
        exit(100)

    # amend kv
    amend_kv_result = util.exec_retry(amend_kv.format(contract_addr, key_position, amend_num))
    if not amend_kv_result.startswith(hex_prefix) or not len(amend_kv_result) == 2 + 64:
        exit(110)

    result = util.get_receipt(amend_kv_result)
    get_kv_result2 = util.exec_retry(get_kv.format(contract_addr, key_position))
    if not get_kv_result2 == amend_num:
        exit(120)
    call_result3 = util.exec_retry(call_fmt.format(contract_addr, '0x0c55699c'))
    if not call_result3 == amend_num:
        exit(130)

    # amend abi
    amend_abi_result = util.exec_retry(amend_abi.format(contract_addr, amend_contract_abi))
    if not amend_abi_result.startswith(hex_prefix) or not len(amend_abi_result) == 2 + 64:
        exit(140)
    result = util.get_receipt(amend_abi_result)

    abi_ressult2 = util.exec_retry(get_abi.format(contract_addr))
    if not abi_ressult2 == amend_contract_abi:
        exit(150)

    # amend balance
    amend_balance_result = util.exec_retry(amend_balance.format(amend_account, amend_num))
    if not amend_balance_result.startswith(hex_prefix) or not len(amend_balance_result) == 2 + 64:
        exit(160)
    result = util.get_receipt(amend_balance_result)

    account_balance = util.exec_retry(get_balance.format(amend_account))
    if not account_balance == amend_num:
        exit(170)
