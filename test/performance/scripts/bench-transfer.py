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


import sys, json, time, subprocess
sys.path.append("test/utils")
import util


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
    tx_hash = util.exec_retry(cmd)
    print("create test contract ret: ", tx_hash)
    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("create test contract failed!")
        exit(10)
    
    time.sleep(9)

    cmd = "cldi -c default get receipt {}"
    ret = util.exec_retry(cmd.format(tx_hash))
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
    
    print('contract_addr: ', contract_addr)

    #deploy batch contract
    '''
pragma solidity ^0.4.24;

/// @title The interface of batch tx
/// @author ["Rivtower Technologies <contact@rivtower.com>"]
interface IBatchTx {
    /// @notice Proxy multiple transactions
    function multiTxs(bytes) external;
}

contract BatchTx is IBatchTx {

    /// @notice Proxy multiple transactions
    ///         The encoded transactions data: tuple(address,dataLen,data)
    ///         dataLen: uint32
    ///         address: uint160
    ///         Example:
    ///             address: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ///             datalen: 00000004
    ///                data: xxxxxxxx
    function multiTxs(bytes)
        external
    {
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            // Ignore the function sig: 0x4
            //        the offset of bytes: 0x20
            //        the len of bytes: 0x20
            let offset := 0x44
            for { } lt(offset, calldatasize) { } {
                // 0xc bytes forward from the offset(0x20-0x14)
                // Use `and` instruction just for safe
                let to := and(calldataload(sub(offset, 0xc)), 0x000000000000000000000000ffffffffffffffffffffffffffffffffffffffff)
                // 0x8 bytes forward from the offset(0x20-0x14-0x4)
                let dataLen := and(calldataload(sub(offset, 0x8)), 0x00000000000000000000000000000000000000000000000000000000ffffffff)
                let ptr := mload(0x40)
                // Jump the address and dataLen(0x14+0x4)
                calldatacopy(ptr, add(offset, 0x18), dataLen)
                switch call(gas, to, 0, ptr, dataLen, ptr, 0)
                case 0 { revert(0, 0) }
                offset := add(add(offset, 0x18), dataLen)
            }
        }
    }
}

$ solc --hashes --bin batch.sol

======= batch.sol:BatchTx =======
Binary:
608060405234801561001057600080fd5b50610111806100206000396000f300608060405260043610603f576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806382cc3327146044575b600080fd5b348015604f57600080fd5b50607a600480360381019080803590602001908201803590602001919091929391929390505050607c565b005b60445b3681101560e05773ffffffffffffffffffffffffffffffffffffffff600c8203351663ffffffff6008830335166040518160188501823760008183836000875af16000811460cb5760d0565b600080fd5b508160188501019350505050607f565b5050505600a165627a7a723058201c9d11ec93b6c7ace99b922b5134ba048259a57756e08789ee872a6c7e3de0d00029
Function signatures:
82cc3327: multiTxs(bytes)

======= batch.sol:IBatchTx =======
Binary:

Function signatures:
82cc3327: multiTxs(bytes)
    '''

    cmd = "cldi -c default create 608060405234801561001057600080fd5b50610111806100206000396000f300608060405260043610603f576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806382cc3327146044575b600080fd5b348015604f57600080fd5b50607a600480360381019080803590602001908201803590602001919091929391929390505050607c565b005b60445b3681101560e05773ffffffffffffffffffffffffffffffffffffffff600c8203351663ffffffff6008830335166040518160188501823760008183836000875af16000811460cb5760d0565b600080fd5b508160188501019350505050607f565b5050505600a165627a7a723058201c9d11ec93b6c7ace99b922b5134ba048259a57756e08789ee872a6c7e3de0d00029"
    tx_hash = util.exec_retry(cmd)
    #print("create batch contract ret: ", tx_hash)
    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("create test contract failed!")
        exit(50)
    
    time.sleep(9)

    cmd = "cldi -c default get receipt {}"
    ret = util.exec_retry(cmd.format(tx_hash))
    if ret.__contains__("Error"):
        print("get receipt failed!")
        exit(60)  

    tx_receipt = json.loads(ret)
    if len(tx_receipt['error_msg']) != 0:
        print("receipt has error!")
        exit(70)        

    batch_contract_addr = tx_receipt['contract_addr']
    if not len(contract_addr) == 42 or not contract_addr.__contains__("0x"):
        print("get contract addr failed!")
        exit(80)

    #print('batch_contract_addr: ', batch_contract_addr)
    
    # adjust quota
    cmd = 'cldi -c default -u admin admin set-quota-limit 1703741824'
    ret = util.exec_retry(cmd.format(tx_hash))
    if ret.__contains__("Error"):
        print("get receipt failed!")
        exit(90)
    
    time.sleep(9)

    # adjust block interval to 1s
    cmd = 'cldi -c default -u admin admin set-block-interval 1'
    ret = util.exec_retry(cmd.format(tx_hash))
    if ret.__contains__("Error"):
        print("get receipt failed!")
        exit(100)
     
    time.sleep(9)

    # build tx data
    addr = contract_addr[2:]
    datalen = '00000004'
    func_hash = '4f2be91f'
    # 100times
    data = (addr + datalen + func_hash) * 100
    
    # encode tx data
    cmd = "cldi -c default ethabi encode params -v bytes 0x{}"
    tx_data = util.exec_retry(cmd.format(data))
    #print("tx data: ", tx_data)

    # bench send
    # tansfer 10000000
    begin_send_time = time.time()
    print('{} - begin to transfer 1000000...'.format(time.strftime('%H:%M:%S',time.localtime(begin_send_time))))
    cmd = "cldi -c default bench send -t {} -d 0x82cc3327{} -c 4 -q 650000 --disable-watch"
    subprocess.Popen(cmd.format(batch_contract_addr, tx_data), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #print('ret: ', ret)

    # calc latency
    amount = 0
    while amount == 0:
        time.sleep(0.5)
        # check amount
        cmd = "cldi -c default call {} 0x06661abd"
        ret = util.exec(cmd.format(contract_addr))
        amount = int(ret, 16)

    begin_amount = amount
    begin_time = time.time()
    print('latency of transfer: %.2f s' %  (begin_time - begin_send_time))

    print('begin to wath amount ...')
    print('begin time {} - begin amount {}'.format(time.strftime('%H:%M:%S',time.localtime(begin_time)), begin_amount))

    print('############################################################################')

    while amount < 1000000:
        time.sleep(1)

        # check amount
        cmd = "cldi -c default call {} 0x06661abd"
        ret = util.exec(cmd.format(contract_addr))
        amount = int(ret, 16)

        now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        print('{} - current amount {}'.format(now, amount))

    print('############################################################################')
    last_time = time.time()
    print('end time {} - end amount {}'.format(time.strftime('%H:%M:%S',time.localtime(last_time)), 1000000))

    # calc tps
    tps = (1000000 - begin_amount) / (last_time - begin_time)
    print("tps: %.2f" % tps)

    # adjust block interval back to 3s
    cmd = 'cldi -c default -u admin admin set-block-interval 3'
    ret = util.exec_retry(cmd.format(tx_hash))
    if ret.__contains__("Error"):
        print("get receipt failed!")
        exit(100)
     
    time.sleep(9)

    exit(0)
