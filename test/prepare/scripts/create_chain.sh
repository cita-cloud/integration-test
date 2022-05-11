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

kubectl get chainconfigs my-chain -ncita
if [ $? -eq 0 ];then
    # delete my-chain
    kubectl delete chainconfigs my-chain -ncita
    # check account all deleted
    times=60
    while [ $times -ge 1 ]
    do
      if [ 0 == `kubectl get accounts.citacloud.rivtower.com -ncita -oyaml | grep 'chain: my-chain' | wc -l` ] && [ 0 == `kubectl get chainnodes.citacloud.rivtower.com -ncita -oyaml | grep 'chainName: my-chain' | wc -l` ] && [ 0 == `kubectl get secrets -ncita | grep my-chain | wc -l` ] && [ 0 == `kubectl get configmaps -ncita | grep my-chain | wc -l` ]; then
        break
      else
        echo "account or node info still exists..."
        let times--
        sleep 1
      fi
    done
    if [ $times -lt 1 ]; then
      echo "wait timeout for delete original account or node info"
      exit 1
    else
      echo "delete original account or node info successful"
    fi
fi

# create admin account by cloud-cli
admin_addr=$(cldi account generate --name admin | jq -r '.address')

# create a chain named my-chain
cco-cli all-in-one create -a $admin_addr my-chain --pullPolicy Always --enableTls --consensusType BFT --nodeCount 4

# wait all pod running
times=300
while [ $times -ge 1 ]
do
  all_run="true"
  if [ `kubectl get pods -ncita --no-headers=true -l app.kubernetes.io/chain-name=my-chain -ojson | jq '.items|length'` == 0 ]; then
    all_run=""
  else
    for status in `kubectl get pods -ncita --no-headers=true -l app.kubernetes.io/chain-name=my-chain | awk '{print $3}'`; do
      if [ $status != "Running" ]; then
        all_run="false"
        break
      fi
    done
  fi
  if [[ $all_run == "true" ]]; then
    break
  else
    echo "wait all pod running..."
    let times--
    sleep 1
  fi
done
if [ $times -lt 1 ]; then
  echo "wait timeout for chain pods, maybe happen some errors"
  exit 1
else
  echo "chain pods are all Running"
fi

# wait for chain start up
echo `date`
sleep 600
