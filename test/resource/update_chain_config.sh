#!/bin/bash

mkdir tmp && cd tmp
echo "update-overlord..."
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config create --chain-name test-chain-overlord --admin 0x9bab5858df4a9e84ff3958884a01a4fce5e07edb --nodelist localhost:40000:node0:k8s,localhost:40001:node1:k8s,localhost:40002:node2:k8s,localhost:40003:node3:k8s --consensus_image consensus_overlord --enable-tx-persistence --exporter-path http://my-bridge-bridge-service:8080
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config append --chain-name test-chain-overlord --node localhost:40004:node4:k8s --enable-tx-persistence --exporter-path http://my-bridge-bridge-service:8080

docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-overlord --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node0 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-overlord --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node1 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-overlord --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node2 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-overlord --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node3 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-overlord --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node4 --disable-health-check --access-mode ReadWriteOnce

rm -f ../overlord/test-chain-overlord-node*/*
cp ./test-chain-overlord-node0/yamls/* ../overlord/test-chain-overlord-node0/
cp ./test-chain-overlord-node1/yamls/* ../overlord/test-chain-overlord-node1/
cp ./test-chain-overlord-node2/yamls/* ../overlord/test-chain-overlord-node2/
cp ./test-chain-overlord-node3/yamls/* ../overlord/test-chain-overlord-node3/
rm -f ../../operations/resource/overlord/test-chain-overlord-node*/*
cp ./test-chain-overlord-node4/yamls/* ../../operations/resource/overlord/test-chain-overlord-node4/

echo "update-raft..."
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config create --chain-name test-chain-raft --admin 0x9bab5858df4a9e84ff3958884a01a4fce5e07edb --nodelist localhost:40000:node0:k8s,localhost:40001:node1:k8s,localhost:40002:node2:k8s,localhost:40003:node3:k8s --consensus_image consensus_raft --access-key-id admin --secret-access-key testtest --s3-endpoint http://minio:9000 --s3-bucket cita-cloud --service-type s3 --s3-root raft --s3-region cn-east-1
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config append --chain-name test-chain-raft --node localhost:40004:node4:k8s --access-key-id admin --secret-access-key testtest --s3-endpoint http://minio:9000 --s3-bucket cita-cloud --service-type s3 --s3-root raft --s3-region cn-east-1

docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-raft --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node0 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-raft --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node1 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-raft --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node2 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-raft --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node3 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-raft --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node4 --disable-health-check --access-mode ReadWriteOnce

rm -f ../raft/test-chain-raft-node*/*
cp ./test-chain-raft-node0/yamls/* ../raft/test-chain-raft-node0/
cp ./test-chain-raft-node1/yamls/* ../raft/test-chain-raft-node1/
cp ./test-chain-raft-node2/yamls/* ../raft/test-chain-raft-node2/
cp ./test-chain-raft-node3/yamls/* ../raft/test-chain-raft-node3/
rm -f ../../operations/resource/raft/test-chain-raft-node*/*
cp ./test-chain-raft-node4/yamls/* ../../operations/resource/raft/test-chain-raft-node4/

cd ..
echo "Done! Pls sudo rm -rf ./tmp"

