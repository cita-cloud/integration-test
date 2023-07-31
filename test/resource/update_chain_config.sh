#!/bin/bash

mkdir tmp && cd tmp
echo "update-zenoh-overlord..."
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config create-k8s --chain-name test-chain-zenoh-overlord --admin 0x9bab5858df4a9e84ff3958884a01a4fce5e07edb --nodelist localhost:40000:node0:k8s,localhost:40001:node1:k8s,localhost:40002:node2:k8s,localhost:40003:node3:k8s --consensus_image consensus_overlord
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config append-k8s --chain-name test-chain-zenoh-overlord --node localhost:40004:node4:k8s

docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-zenoh-overlord --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node0 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-zenoh-overlord --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node1 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-zenoh-overlord --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node2 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-zenoh-overlord --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node3 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-zenoh-overlord --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node4 --disable-health-check --access-mode ReadWriteOnce

rm -f ../zenoh-overlord/test-chain-zenoh-overlord-node*/*
cp ./test-chain-zenoh-overlord-node0/yamls/* ../zenoh-overlord/test-chain-zenoh-overlord-node0/
cp ./test-chain-zenoh-overlord-node1/yamls/* ../zenoh-overlord/test-chain-zenoh-overlord-node1/
cp ./test-chain-zenoh-overlord-node2/yamls/* ../zenoh-overlord/test-chain-zenoh-overlord-node2/
cp ./test-chain-zenoh-overlord-node3/yamls/* ../zenoh-overlord/test-chain-zenoh-overlord-node3/
rm -f ../../operations/resource/zenoh-overlord/test-chain-zenoh-overlord-node*/*
cp ./test-chain-zenoh-overlord-node4/yamls/* ../../operations/resource/zenoh-overlord/test-chain-zenoh-overlord-node4/

echo "update-zenoh-raft..."
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config create-k8s --chain-name test-chain-zenoh-raft --admin 0x9bab5858df4a9e84ff3958884a01a4fce5e07edb --nodelist localhost:40000:node0:k8s,localhost:40001:node1:k8s,localhost:40002:node2:k8s,localhost:40003:node3:k8s --consensus_image consensus_raft
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config append-k8s --chain-name test-chain-zenoh-raft --node localhost:40004:node4:k8s

docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-zenoh-raft --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node0 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-zenoh-raft --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node1 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-zenoh-raft --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node2 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-zenoh-raft --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node3 --disable-health-check --access-mode ReadWriteOnce
docker run -it --rm -v $(pwd):/data -w /data registry.devops.rivtower.com/cita-cloud/cloud-config cloud-config update-yaml --chain-name test-chain-zenoh-raft --docker-registry registry.devops.rivtower.com --docker-repo cita-cloud --pull-policy Always --storage-class nfs-client --domain node4 --disable-health-check --access-mode ReadWriteOnce

rm -f ../zenoh-raft/test-chain-zenoh-raft-node*/*
cp ./test-chain-zenoh-raft-node0/yamls/* ../zenoh-raft/test-chain-zenoh-raft-node0/
cp ./test-chain-zenoh-raft-node1/yamls/* ../zenoh-raft/test-chain-zenoh-raft-node1/
cp ./test-chain-zenoh-raft-node2/yamls/* ../zenoh-raft/test-chain-zenoh-raft-node2/
cp ./test-chain-zenoh-raft-node3/yamls/* ../zenoh-raft/test-chain-zenoh-raft-node3/
rm -f ../../operations/resource/zenoh-raft/test-chain-zenoh-raft-node*/*
cp ./test-chain-zenoh-raft-node4/yamls/* ../../operations/resource/zenoh-raft/test-chain-zenoh-raft-node4/

cd ..
echo "Done! Pls sudo rm -rf ./tmp"

