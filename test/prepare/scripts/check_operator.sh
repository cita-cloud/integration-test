#!/bin/bash
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
#
#

# add repo
helm repo add cita-node-operator https://cita-cloud.github.io/cita-node-operator

res=`helm list -ncita`
if [ $? -ne 0 ]; then
  exit 1
fi
if [ 1 == `echo "${res}" | grep cita-node-operator | wc -l` ]; then
  echo "cita-node-operator has installed"
else
  echo "please install cita-node-operator first"
  exit 2
fi