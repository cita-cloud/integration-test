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
import subprocess, json, time

DEFAULT_QUOTA_LIMIT = 1073741824
NEW_QUOTA_LIMIT = 500000000
hex_prefix = '0x'


def is_json(res):
    try:
        json.loads(res)
    except ValueError:
        return False
    return True


def get_system_config():
    # get system-config
    result = subprocess.getoutput("cldi -c default get system-config")
    if not is_json(result):
        print("get system-config failed: {}", result)
        exit(10)
    return json.loads(result)


def set_quota_limit():
    set_cmd = "cldi -c default -u admin admin set-quota-limit {}".format(NEW_QUOTA_LIMIT)
    tx_hash = subprocess.getoutput(set_cmd)
    if not tx_hash.__contains__(hex_prefix) or not len(tx_hash) == len(hex_prefix) + 64:
        print("set-quota-limit failed!")
        exit(20)
    get_cmd = "cldi -c default get tx {}"
    cmd_result = subprocess.getoutput(get_cmd.format(tx_hash))
    if cmd_result.__contains__("Error"):
        print("get set-quota-limit tx failed")
        exit(30)
    return tx_hash


if __name__ == "__main__":
    # get system-config
    old_quota_limit = get_system_config()['quota_limit']
    if not old_quota_limit == DEFAULT_QUOTA_LIMIT:
        print("invalid quota limit: ", old_quota_limit)
        exit(10)

    # set quota limit to 500000000
    tx_hash = set_quota_limit()

    time.sleep(6)

    # check new quota limit in system-config
    system_config = get_system_config()
    new_quota_limit = system_config['quota_limit']
    if not new_quota_limit == NEW_QUOTA_LIMIT:
        print("quota limit mismatch")
        exit(40)

    if system_config['quota_limit_pre_hash'] != tx_hash:
        print("set-quota-limit tx hash mismatch!")
        exit(50)

    # verify quota limit
    time.sleep(30)
    send_cmd = "send 0xf064e32407b6cc412fe33f6ba55f578ac413ecdc 0x4f2be91f -q {}"
    result = subprocess.getoutput(send_cmd.format(NEW_QUOTA_LIMIT + 1))
    if result is None or not result.__contains__('QuotaUsedExceed'):
        print("verify invalid quota failed: {}!", result)
        exit(60)

    result = subprocess.getoutput(send_cmd.format(NEW_QUOTA_LIMIT))
    if result is None or not result.startswith(hex_prefix) or len(result) != len(hex_prefix) + 64:
        print("verify valid quota failed: {}!", result)
        exit(60)

    exit(0)