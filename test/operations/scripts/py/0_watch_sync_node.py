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
import threading
import time
import sys

sys.path.append("test/utils")
import util
from logger import logger

def watch_bn():
    bn = util.get_node_block_number("default")
    result = 0
    while result <= bn:
        time.sleep(10)
        logger.debug("syncing node block-number: {result} ... {bn}".format(result=result, bn=bn))
        try:
            result = util.get_node_block_number("node4")
        except Exception as e:
            logger.debug("Error occurred while getting node block number: {e}".format(e=e))
            pass

    logger.info("synced node block-number: {result} > {bn}".format(result=result, bn=bn))
    exit(0)


if __name__ == '__main__':
    t = threading.Thread(target=watch_bn)
    t.daemon = True
    t.start()
    t.join(timeout=600)
    if t.is_alive():
        logger.info("sync timeout")
        exit(1)
    exit(0)
