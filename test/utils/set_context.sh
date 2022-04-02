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

# randomly get the service name of a node
service_name=`kubectl get svc -ncita --no-headers=true -l app.kubernetes.io/chain-name=my-chain | head -n 1 | awk '{print $1}'`
cldi -r $service_name.cita:50004 -e $service_name.cita:50002 -u default context save default