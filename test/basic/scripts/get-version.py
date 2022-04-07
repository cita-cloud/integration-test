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

import subprocess, re

pattern = r'\d+\.(?:\d+\.)\d+'


def is_version(result):
    return re.match(pattern, result)


if __name__ == "__main__":
    print(11111111)
    result = subprocess.getoutput("cldi get version")
    if is_version(result):
        exit(0)
    exit(1)
