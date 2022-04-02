# integration-testing
### Validate Jenkinsfile Syntax
---
- curl --user username:password -X POST -F "jenkinsfile=<Jenkinsfile" http://jenkins-url:8080/pipeline-model-converter/validate

or
- use Jenkins Pipeline Linter Connector for Visual Studio Code
