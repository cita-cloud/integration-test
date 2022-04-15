#!/usr/bin/python
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


import subprocess, sys, json, time

if __name__ == "__main__":
    # deploy test contract
    '''
$ cat Counter.sol 
pragma solidity ^0.4.24;

contract Counter {
    uint public count;
    
    function add() public {
        count += 1;
    }
    
    function reset() public {
        count = 0;
    }
}

$ curl -o solc -L https://github.com/ethereum/solidity/releases/download/v0.4.24/solc-static-linux
$ chmod +x solc
$ sudo mv ./solc /usr/local/bin/
$ solc --hashes --bin Counter.sol 

======= Counter.sol:Counter =======
Binary: 
608060405234801561001057600080fd5b5060f58061001f6000396000f3006080604052600436106053576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806306661abd1460585780634f2be91f146080578063d826f88f146094575b600080fd5b348015606357600080fd5b50606a60a8565b6040518082815260200191505060405180910390f35b348015608b57600080fd5b50609260ae565b005b348015609f57600080fd5b5060a660c0565b005b60005481565b60016000808282540192505081905550565b600080819055505600a165627a7a72305820a841f5848c8c68bc957103089b41e192a79aed7ac2aebaf35ae1e36469bd44d90029
Function signatures: 
4f2be91f: add()
06661abd: count()
d826f88f: reset()
    '''
    cmd = "cldi -c default create 608060405234801561001057600080fd5b5060f58061001f6000396000f3006080604052600436106053576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806306661abd1460585780634f2be91f146080578063d826f88f146094575b600080fd5b348015606357600080fd5b50606a60a8565b6040518082815260200191505060405180910390f35b348015608b57600080fd5b50609260ae565b005b348015609f57600080fd5b5060a660c0565b005b60005481565b60016000808282540192505081905550565b600080819055505600a165627a7a72305820a841f5848c8c68bc957103089b41e192a79aed7ac2aebaf35ae1e36469bd44d90029"
    tx_hash = subprocess.getoutput(cmd)
    print("create test contract ret: ", tx_hash)
    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("create test contract failed!")
        exit(10)
    
    time.sleep(9)

    cmd = "cldi -c default get receipt {}"
    ret = subprocess.getoutput(cmd.format(tx_hash))
    if ret.__contains__("Error"):
        print("get receipt failed!")
        exit(20)  

    tx_receipt = json.loads(ret)
    if len(tx_receipt['error_msg']) != 0:
        print("receipt has error!")
        exit(30)        

    contract_addr = tx_receipt['contract_addr']
    if not len(contract_addr) == 42 or not contract_addr.__contains__("0x"):
        print("get contract addr failed!")
        exit(40)


    # bench call
    cmd = "cldi -c default bench call -t {} -d 06661abd"
    ret = subprocess.getoutput(cmd.format(contract_addr))

    # calc tps
    begin_pos = ret.find('`10000` tasks finished in `') + 27
    time_len = ret[begin_pos:].find('` ms')
    t_ms = int(ret[begin_pos:begin_pos + time_len])

    tps = 10000 * 1000 / t_ms
    print("tps: ", int(tps))

    time.sleep(30)

    exit(0)
