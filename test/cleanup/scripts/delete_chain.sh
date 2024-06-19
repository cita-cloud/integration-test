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
kubectl delete -f test/resource/$CHAIN_TYPE -n $NAMESPACE --recursive
kubectl delete -f test/operations/resource/$CHAIN_TYPE -n $NAMESPACE --recursive



kubectl delete pvc -n $NAMESPACE -l app.kubernetes.io/chain-name=$CHAIN_NAME

if [ "$CHAIN_TYPE" = "raft" ]; then
    kubectl delete -f test/resource/minio.yaml -n $NAMESPACE --request-timeout=30s
    kubectl delete pvc datadir-minio-0 -n $NAMESPACE --request-timeout=30s
fi

if [ "$CHAIN_TYPE" = "overlord" ]; then
    # delete strimzi kafka and kafka-bridge
    sed -i "s/xxxxxx/$NAMESPACE/g" test/resource/kafka/strimzi.yaml
    sed -i "s/xxxxxx/$SC/g" test/resource/kafka/kafka-single-node.yaml
    kubectl delete -f test/resource/kafka/kafka-bridge.yaml -n $NAMESPACE --request-timeout=30s
    kubectl delete -f test/resource/kafka/kafka-single-node.yaml -n $NAMESPACE --request-timeout=30s
    kubectl delete -f test/resource/kafka/strimzi.yaml -n $NAMESPACE --request-timeout=30s
    kubectl delete pvc data-0-my-cluster-dual-role-0 -n $NAMESPACE --request-timeout=30s

    # delete doris
    sed -i "s/xxxxxx/$NAMESPACE/g" test/resource/doris/operator.yaml
    sed -i "s/xxxxxx/$SC/g" test/resource/doris/doriscluster-sample-storageclass.yaml
    kubectl delete -f test/resource/doris/doriscluster-sample-storageclass.yaml -n $NAMESPACE --request-timeout=30s
    kubectl delete -f test/resource/doris/operator.yaml --request-timeout=30s
    kubectl delete -f test/resource/doris/doris.selectdb.com_dorisclusters.yaml --request-timeout=30s
    kubectl delete pvc belog-doriscluster-sample-storageclass1-be-0 -n $NAMESPACE --request-timeout=30s
    kubectl delete pvc betest-doriscluster-sample-storageclass1-be-0 -n $NAMESPACE --request-timeout=30s
    kubectl delete pvc felog-doriscluster-sample-storageclass1-fe-0 -n $NAMESPACE --request-timeout=30s
    kubectl delete pvc fetest-doriscluster-sample-storageclass1-fe-0 -n $NAMESPACE --request-timeout=30s
fi
