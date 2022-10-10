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
  # install cita-node-operator
  echo "installing cita-node-operator..."
  helm install cita-node-operator cita-node-operator/cita-node-operator -n=cita

  # check cita-node-operator pod running
  times=300
  while [ $times -ge 0 ]
  do
    pod_res=`kubectl get pod --no-headers=true -ncita -l app.kubernetes.io/name=cita-node-operator --request-timeout=10s`
    if [ $? -ne 0 ]; then
      let times--
      continue
    fi
    if [ 1 == `echo "${pod_res}" | grep Running | wc -l` ]; then
      break
    else
      echo "cita-node-operator pod's status is not Running, waiting..."
      let times--
      sleep 3
    fi
  done
  if [ $times -lt 0 ]; then
    echo "waiting cita-node-operator timeout."
    exit 2
  fi
  echo "cita-node-operator has installed."
fi