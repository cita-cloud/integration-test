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

# check pod
times=60
while [ $times -ge 0 ]
do
  if [ 0 == `kubectl get pod --no-headers=true -ncita $CHAIN_NAME'-node4-0' | wc -l` ]; then
    break
  else
    echo "old node4 resource still exists, delete it..."
    # delete command maybe return errors, ignore
    kubectl delete -f test/operations/resource/$CHAIN_TYPE -n cita --recursive>/dev/null
    let times--
    sleep 5
  fi
done
# check pvc
times=60
while [ $times -ge 0 ]
do
  if [ 0 == `kubectl get pvc --no-headers=true -ncita 'datadir-'$CHAIN_NAME'-node4-0' | wc -l` ]; then
    break
  else
    echo "old node4 pvc still exists, delete it..."
    kubectl delete pvc -ncita 'datadir-'$CHAIN_NAME'-node4-0' 2>/dev/null
    let times--
    sleep 5
  fi
done
# append node
echo "append $CHAIN_TYPE sync node"
kubectl apply -f test/operations/resource/$CHAIN_TYPE -n cita --recursive

# check all pod's status is RUNNING
times=300
while [ $times -ge 0 ]
do
  if [ 5 == `kubectl get pod --no-headers=true -ncita -l app.kubernetes.io/chain-name=$CHAIN_NAME | grep Running | wc -l` ]; then
    # all pod is Running
    break
  else
    echo "pod's status is not Running, waiting..."
    let times--
    sleep 3
  fi
done

# wait half of minute
echo `date`
sleep 30

service_name=`kubectl get svc -ncita --no-headers=true -l app.kubernetes.io/chain-name=$CHAIN_NAME  | head -n 5 | tail -n 1 | awk '{print $1}'`
cldi -r $service_name.cita:50004 -e $service_name.cita:50002 -u default context save node4
