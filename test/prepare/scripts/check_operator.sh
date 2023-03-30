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

# check cita-node-operator
res=`kubectl get deployments.apps cita-node-operator -n $NAMESPACE  -o jsonpath='{.spec.replicas}'`
if [ $? -eq 0 ]; then
  if [ ${res} -eq 0 ]; then
    echo "scale up cita-node-operator replica to 1..."
    kubectl scale deployments.apps cita-node-operator --replicas=1 -n $NAMESPACE
  else
    echo "cita-node-operator's replica is already 1"
  fi
else
  echo "get operator deployment happens error, please check it!"
fi

# check k8up-operator
res=`kubectl get deployments.apps k8up -n $NAMESPACE  -o jsonpath='{.spec.replicas}'`
if [ $? -eq 0 ]; then
  if [ ${res} -eq 0 ]; then
    echo "scale up k8up-operator replica to 1..."
    kubectl scale deployments.apps k8up --replicas=1 -n $NAMESPACE
  else
    echo "k8up-operator's replica is already 1"
  fi
else
  echo "get operator deployment happens error, please check it!"
fi