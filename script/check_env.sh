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

set -o errexit

if [ "`kubectl get deployment cita-cloud-operator -ncita -ojson | jq '.status.availableReplicas'`" == "1" ]; then
    echo "cita-cloud-operator is running"
else
  echo "cita-cloud-operator is not running"
  exit 1
fi

if [ "`kubectl get deployment cita-cloud-operator-proxy -ncita -ojson | jq '.status.availableReplicas'`" == "1" ]; then
    echo "cita-cloud-operator-proxy is running"
else
  echo "cita-cloud-operator-proxy is not running"
  exit 1
fi