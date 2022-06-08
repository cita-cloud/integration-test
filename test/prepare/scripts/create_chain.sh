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

# admin account import
echo 'import admin account'
cldi account import 0xb2371a70c297106449f89445f20289e6d16942f08f861b5e95cbcf0462e384c1 --name admin --crypto SM

if [ $CHAIN_TYPE == "tls-bft" ]; then
  # check pod
  times=60
  while [ $times -ge 0 ]
  do
    if [ 0 == `kubectl get pod --no-headers=true -ncita -l app.kubernetes.io/chain-name=$CHAIN_NAME | wc -l` ]; then
      break
    else
      echo "old chain resource still exists, delete it..."
      # delete command maybe return errors, ignore
      kubectl delete -f test/resource/tls-bft --recursive 2>/dev/null
      let times--
      sleep 5
    fi
  done
  # check pvc
  times=60
  while [ $times -ge 0 ]
  do
    if [ 0 == `kubectl get pvc --no-headers=true -ncita -l app.kubernetes.io/chain-name=$CHAIN_NAME | wc -l` ]; then
      break
    else
      echo "old chain pvc still exists, delete it..."
      kubectl delete pvc -ncita -l app.kubernetes.io/chain-name=$CHAIN_NAME 2>/dev/null
      let times--
      sleep 5
    fi
  done
  # create chain
  echo "create tls-bft chain"
  kubectl apply -f test/resource/tls-bft --recursive
elif [ $CHAIN_TYPE == "tls-raft" ]; then
  # check pod
  times=60
  while [ $times -ge 0 ]
  do
    if [ 0 == `kubectl get pod --no-headers=true -ncita -l app.kubernetes.io/chain-name=$CHAIN_NAME | wc -l` ]; then
      break
    else
      echo "old chain resource still exists, delete it..."
      # delete command maybe return errors, ignore
      kubectl delete -f test/resource/tls-raft --recursive 2>/dev/null
      let times--
      sleep 5
    fi
  done
  # check pvc
  times=60
  while [ $times -ge 0 ]
  do
    if [ 0 == `kubectl get pvc --no-headers=true -ncita -l app.kubernetes.io/chain-name=$CHAIN_NAME | wc -l` ]; then
      break
    else
      echo "old chain pvc still exists, delete it..."
      kubectl delete pvc -ncita -l app.kubernetes.io/chain-name=$CHAIN_NAME 2>/dev/null
      let times--
      sleep 5
    fi
  done
  # create chain
  echo "create tls-raft chain"
  kubectl apply -f test/resource/tls-raft --recursive
fi

# check all pod's status is RUNNING
times=300
while [ $times -ge 0 ]
do
  if [ 4 == `kubectl get pod --no-headers=true -ncita -l app.kubernetes.io/chain-name=$CHAIN_NAME | grep Running | wc -l` ]; then
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