# integration-testing
### Validate Jenkinsfile Syntax
---
- curl --user username:password -X POST -F "jenkinsfile=<Jenkinsfile" http://jenkins-url:8080/pipeline-model-converter/validate

or
- use Jenkins Pipeline Linter Connector for Visual Studio Code

# test with exsited chain

```
$ git clone https://gitee.com/cita-cloud/integration-test.git
$ cd integration-test
$ docker run -it --rm -v $(pwd):/data -v ~/.kube:/root/.kube -w /data -e CHAIN_NAME=`your chain name` -e CHAIN_TYPE=`your chain type` -e NAMESPACE=`chain's namespace` -e SC=`storageclass` registry.devops.rivtower.com/cita-cloud/test-ci:v0.0.1 bash

# kubectl get nodes
# bash port_forward.sh &
# cldi account import 0xb2371a70c297106449f89445f20289e6d16942f08f861b5e95cbcf0462e384c1 --name admin --crypto SM
# cldi -r 127.0.0.1:50004 -e 127.0.0.1:50002 -u default context save default
# cldi get bn
2565

# bash manual_run.sh
```