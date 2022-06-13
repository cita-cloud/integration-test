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

# delete chain resource
if [ $CHAIN_TYPE == "tls-bft" ]; then
  kubectl delete -f test/resource/tls-bft -ncita --recursive
elif [ $CHAIN_TYPE == "tls-raft" ]; then
  kubectl delete -f test/resource/tls-raft -ncita --recursive
elif [ $CHAIN_TYPE == "tls-overlord" ]; then
  kubectl delete -f test/resource/tls-overlord -ncita --recursive
fi

kubectl delete pvc -ncita -l app.kubernetes.io/chain-name=$CHAIN_NAME
