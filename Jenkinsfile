pipeline {
  agent {
    docker {
      image 'python:3.8'
    }

  }
  stages {
    stage('Checkout') {
      steps {
        checkout([$class: 'GitSCM',
        branches: [[name: GIT_BUILD_REF]],
        userRemoteConfigs: [[
          url: GIT_REPO_URL,
          credentialsId: CREDENTIALS_ID
        ]]])
      }
    }

    stage('Remote Deploy') {
      steps {
        sh 'apt-get -y install -f sshpass'
        sh 'sshpass -p ${SERVER_PASSWORD} ssh ${SERVER_USERNAME}@${SERVER_HOST}'
        sh 'ls'
      }
    }

  }
}