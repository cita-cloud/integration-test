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

kubectl create namespace $NAMESPACE

if [ "$CHAIN_TYPE" = "raft" ]; then
    # recreate s3:minio
    sed -i "s/xxxxxx/$SC/g" test/resource/minio.yaml
    kubectl delete -f test/resource/minio.yaml -n $NAMESPACE --request-timeout=30s
    kubectl delete pvc datadir-minio-0 -n $NAMESPACE --request-timeout=30s
    kubectl apply -f test/resource/minio.yaml -n $NAMESPACE --request-timeout=30s
fi

if [ "$CHAIN_TYPE" = "overlord" ]; then
    # recreate strimzi kafka and kafka-bridge
    sed -i "s/xxxxxx/$NAMESPACE/g" test/resource/kafka/strimzi.yaml
    sed -i "s/xxxxxx/$SC/g" test/resource/kafka/kafka-single-node.yaml
    kubectl delete -f test/resource/kafka/kafka-bridge.yaml -n $NAMESPACE --request-timeout=30s
    kubectl delete -f test/resource/kafka/kafka-single-node.yaml -n $NAMESPACE --request-timeout=30s
    kubectl delete -f test/resource/kafka/strimzi.yaml -n $NAMESPACE --request-timeout=30s
    kubectl delete pvc data-0-my-cluster-dual-role-0 -n $NAMESPACE --request-timeout=30s

    kubectl create -f test/resource/kafka/strimzi.yaml -n $NAMESPACE --request-timeout=30s
    kubectl wait deployment/strimzi-cluster-operator --for=condition=Available=True --timeout=300s -n $NAMESPACE
    kubectl apply -f test/resource/kafka/kafka-single-node.yaml -n $NAMESPACE --request-timeout=30s
    kubectl wait kafka/my-cluster --for=condition=Ready --timeout=300s -n $NAMESPACE
    kubectl apply -f test/resource/kafka/kafka-bridge.yaml -n $NAMESPACE --request-timeout=30s
    kubectl wait KafkaBridge/my-bridge --for=condition=Ready --timeout=300s -n $NAMESPACE

    # create kafka topic
    kubectl exec -n $NAMESPACE -it my-cluster-dual-role-0 -c kafka -- bin/kafka-topics.sh --create --topic cita-cloud.test-chain-overlord.blocks --bootstrap-server my-cluster-kafka-bootstrap:9092
    kubectl exec -n $NAMESPACE -it my-cluster-dual-role-0 -c kafka -- bin/kafka-topics.sh --create --topic cita-cloud.test-chain-overlord.txs --bootstrap-server my-cluster-kafka-bootstrap:9092
    kubectl exec -n $NAMESPACE -it my-cluster-dual-role-0 -c kafka -- bin/kafka-topics.sh --create --topic cita-cloud.test-chain-overlord.utxos --bootstrap-server my-cluster-kafka-bootstrap:9092
    kubectl exec -n $NAMESPACE -it my-cluster-dual-role-0 -c kafka -- bin/kafka-topics.sh --create --topic cita-cloud.test-chain-overlord.system-config --bootstrap-server my-cluster-kafka-bootstrap:9092
    kubectl exec -n $NAMESPACE -it my-cluster-dual-role-0 -c kafka -- bin/kafka-topics.sh --create --topic cita-cloud.test-chain-overlord.receipts --bootstrap-server my-cluster-kafka-bootstrap:9092
    kubectl exec -n $NAMESPACE -it my-cluster-dual-role-0 -c kafka -- bin/kafka-topics.sh --create --topic cita-cloud.test-chain-overlord.logs --bootstrap-server my-cluster-kafka-bootstrap:9092

    # recreate doris
    sed -i "s/xxxxxx/$NAMESPACE/g" test/resource/doris/operator.yaml
    sed -i "s/xxxxxx/$SC/g" test/resource/doris/doriscluster-sample-storageclass.yaml
    kubectl delete -f test/resource/doris/doriscluster-sample-storageclass.yaml -n $NAMESPACE --request-timeout=30s
    kubectl delete -f test/resource/doris/operator.yaml --request-timeout=30s
    kubectl delete -f test/resource/doris/doris.selectdb.com_dorisclusters.yaml --request-timeout=30s
    kubectl delete pvc belog-doriscluster-sample-storageclass1-be-0 -n $NAMESPACE --request-timeout=30s
    kubectl delete pvc betest-doriscluster-sample-storageclass1-be-0 -n $NAMESPACE --request-timeout=30s
    kubectl delete pvc felog-doriscluster-sample-storageclass1-fe-0 -n $NAMESPACE --request-timeout=30s
    kubectl delete pvc fetest-doriscluster-sample-storageclass1-fe-0 -n $NAMESPACE --request-timeout=30s

    kubectl create -f test/resource/doris/doris.selectdb.com_dorisclusters.yaml --request-timeout=30s
    kubectl apply -f test/resource/doris/operator.yaml --request-timeout=30s
    kubectl wait deployment/doris-operator --for=condition=Available=True --timeout=300s -n $NAMESPACE
    kubectl apply -f test/resource/doris/doriscluster-sample-storageclass.yaml -n $NAMESPACE --request-timeout=30s
    sleep 30
    kubectl wait pod/doriscluster-sample-storageclass1-fe-0 --for=condition=Ready=True --timeout=600s -n $NAMESPACE
    sleep 30
    kubectl wait pod/doriscluster-sample-storageclass1-be-0 --for=condition=Ready=True --timeout=600s -n $NAMESPACE

    # wait 5min for doris be connect to fe 
    sleep 300

    # create table and load routine
    sed -i "s/xxxxxx/$CHAIN_NAME/g" test/resource/doris/kafka-load.sql
    mysql -h doriscluster-sample-storageclass1-fe-internal.$NAMESPACE.svc.cluster.local -P 9030 -u root -e "SOURCE test/resource/doris/kafka-load.sql"
fi


# check pod
times=60
while [ $times -ge 0 ]
do
  res=`kubectl get sts --no-headers=true -n $NAMESPACE -l app.kubernetes.io/chain-name=$CHAIN_NAME --request-timeout=10s`
  if [ $? -ne 0 ]; then
    let times--
    continue
  fi
  if [ 0 == `echo "${res}" | sed '/^$/d' | wc -l` ]; then
    break
  else
    echo "old chain resource still exists, delete it..."
    # delete command maybe return errors, ignore
    kubectl delete -f test/resource/$CHAIN_TYPE -n $NAMESPACE --request-timeout=10s --recursive 2>/dev/null
    kubectl delete -f test/operations/resource/$CHAIN_TYPE -n $NAMESPACE --request-timeout=10s --recursive 2>/dev/null
    let times--
    sleep 5
  fi
done
# check pvc
times=60
while [ $times -ge 0 ]
do
  res=`kubectl get pvc --no-headers=true -n $NAMESPACE -l app.kubernetes.io/chain-name=$CHAIN_NAME --request-timeout=10s`
  if [ $? -ne 0 ]; then
    let times--
    continue
  fi
  if [ 0 == `echo "${res}" | sed '/^$/d' | wc -l` ]; then
    break
  else
    echo "old chain pvc still exists, delete it..."
    kubectl delete pvc -n $NAMESPACE -l app.kubernetes.io/chain-name=$CHAIN_NAME --request-timeout=10s 2>/dev/null
    let times--
    sleep 5
  fi
done

# create chain
echo "create $CHAIN_TYPE chain"
kubectl apply -f test/resource/$CHAIN_TYPE -n $NAMESPACE --recursive --request-timeout=30s
if [ $? -ne 0 ]; then
  echo "create $CHAIN_TYPE chain failed"
  exit 1
fi

# check all pod's status is RUNNING
times=300
while [ $times -ge 0 ]
do
  res=`kubectl get pod --no-headers=true -n $NAMESPACE -l app.kubernetes.io/chain-name=$CHAIN_NAME --request-timeout=10s`
  if [ $? -ne 0 ]; then
    let times--
    continue
  fi
  if [ 4 == `echo "${res}" | grep Running | wc -l` ]; then
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

service_name=`kubectl get svc -n $NAMESPACE --no-headers=true -l app.kubernetes.io/chain-name=$CHAIN_NAME --request-timeout=10s | head -n 1 | awk '{print $1}'`
cldi -r $service_name.$NAMESPACE:50004 -e $service_name.$NAMESPACE:50002 -u default context save default
