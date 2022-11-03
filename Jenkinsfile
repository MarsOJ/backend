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
        sh 'wget http://sourceforge.net/projects/sshpass/files/latest/download -O sshpass.tar.gz && tar -zxvf sshpass.tar.gz && cd sshpass-1.08 && ./configure && make && make install'
        sh 'sshpass -p ${SERVER_PASSWORD} ssh -t -t ${SERVER_USERNAME}@${SERVER_HOST} ls && exit'
      }
    }

  }
}