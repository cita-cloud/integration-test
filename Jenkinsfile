pipeline {
  agent {
    kubernetes {
      cloud 'kubernetes/rivtower-developing-120'
      yamlFile 'k8s/declarativeYamlFile.yml'
    }
  }

  stages {

    stage('Print Cli Version') {
      steps {
        container('cli') {
          sh 'cldi -V'
        }
      }
    }

    stage('Prepare') {
      steps {
        container('cli') {
          sh 'test/prepare/startup.sh'
        }
      }
    }

    stage('Basic Test') {
      steps {
        container('cli') {
          sh 'test/basic/startup.sh'
        }
      }
    }

    stage('Governance Test') {
      steps {
        container('cli') {
          sh 'test/governance/startup.sh'
        }
      }
    }

    stage('Performance Test') {
      steps {
        container('cli') {
          sh 'test/performance/startup.sh'
        }
      }
    }

    stage('Reliability Test') {
      steps {
        container('cli') {
          sh 'test/reliability/startup.sh'
        }
      }
    }

    stage('Security Test') {
      steps {
        container('cli') {
          sh 'test/security/startup.sh'
        }
      }
    }

    stage('Compatibility Test') {
      steps {
        container('cli') {
          sh 'test/compatibility/startup.sh'
        }
      }
    }

    stage('Operations Test') {
      steps {
        container('cli') {
          sh 'test/operations/startup.sh'
        }
      }
    }

    stage('K8s Operator Test') {
      steps {
        container('cli') {
          sh 'test/operator/startup.sh'
        }
      }
    }
  }

  post {
    success {
      container('cli') {
        sh 'test/cleanup/startup.sh'
        sh "test/utils/send_msg.sh success"
      }
    }
    failure {
      container('cli') {
        sh "test/utils/send_msg.sh failure"
      }
    }
  }
}
