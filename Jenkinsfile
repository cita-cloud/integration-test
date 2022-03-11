pipeline {
  agent {
    kubernetes {
      yamlFile 'script/declarativeYamlFile.yml'
    }
  }

  stages {

    stage('Print cli version') {
      steps {
        container('cli') {
          sh 'cco-cli version'
          sh 'cldi -h'
        }
      }
    }

    stage('Check env') {
      steps {
        container('cli') {
          sh 'script/check_env.sh'
        }
      }
    }

    stage('Create a chain') {
      steps {
        container('cli') {
          sh 'cco-cli all-in-one create my-chain'
        }
      }
    }

  }
}
