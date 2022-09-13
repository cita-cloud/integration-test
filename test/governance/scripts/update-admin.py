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

if __name__ == "__main__":
    cmd = "cldi account list"
    cmd_result = util.exec(cmd)
    account_list = json.loads(cmd_result)

    # find admin account
    for account in account_list:
        print("account: ", account)
        if account['name'] == "admin":
            admin_addr = account['address']

    print("find admin account: ", admin_addr)
    
    # check admin in system-config
    cmd = "cldi -c default get system-config"
    cmd_result = util.exec(cmd)
    system_config = json.loads(cmd_result)
    admin = system_config['admin']
    admin_hash = system_config['admin_pre_hash']

    if admin != admin_addr:
        print("admin account mismatch!", admin, admin_addr)
        exit(10)

    # create new admin account 
    util.exec("cldi account delete -y new_admin")
    cmd = "cldi account generate --name new_admin"
    cmd_result = util.exec(cmd)
    new_admin = json.loads(cmd_result)
    new_admin_addr = new_admin['address']

    # set new admin account
    cmd = "cldi -c default -u admin admin update-admin {}"
    tx_hash = util.exec(cmd.format(new_admin_addr))
    print("update-admin ret:", tx_hash)

    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("update-admin failed!")
        exit(20)

    util.get_tx(tx_hash)

    # check admin in system-config
    cmd = "cldi -c default get system-config"
    cmd_result = util.exec(cmd)
    system_config = json.loads(cmd_result)
    admin = system_config['admin']
    admin_hash = system_config['admin_pre_hash']

    if admin != new_admin_addr:
        print("new admin account mismatch!", admin, new_admin_addr)
        exit(40)

    if admin_hash != tx_hash:
        print("update-admin tx hash mismatch!", admin_hash, tx_hash)
        exit(50)

    # reset to old admin account
    cmd = "cldi -c default -u new_admin admin update-admin {}"
    tx_hash = util.exec(cmd.format(admin_addr))
    print("update-admin ret:", tx_hash)

    if not len(tx_hash) == 66 or not tx_hash.__contains__("0x"):
        print("update-admin failed!")
        exit(60)

    util.get_tx(tx_hash)

    # check admin in system-config
    cmd = "cldi -c default get system-config"
    cmd_result = util.exec(cmd)
    system_config = json.loads(cmd_result)
    admin = system_config['admin']
    admin_hash = system_config['admin_pre_hash']

    if admin != admin_addr:
        print("new admin account mismatch!", admin, admin_addr)
        exit(80)

    if admin_hash != tx_hash:
        print("update-admin tx hash mismatch!", admin_hash, tx_hash)
        exit(90)

    exit(0)
