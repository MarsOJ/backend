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

    stage('Install Independencies') {
      steps {
        sh 'python -m pip install --upgrade pip && pip install flake8 flake8-bugbear flake8-import-order pytest  &&     if [ -f requirements.txt ]; then pip install -r requirements.txt; fi'
      }
    }

    stage('Install MongoDB'){
      steps{
        sh 'wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel80-5.0.4.tgz'
        sh 'mkdir /usr/local/mongodb'
        sh 'tar -zxvf mongodb-linux-x86_64-rhel80-5.0.4.tgz -C /usr/local/mongodb'
        sh 'cd /usr/local/mongodb'
        sh 'ls'
        sh 'mv mongodb-linux-x86_64-rhel80-5.0.4 mongodbserver'
        sh 'mkdir -p /var/lib/mongo'
        sh 'mkdir -p /var/log/mongodb'
        sh 'chmod 777 /var/lib/mongo'
        sh 'chmod 777 /var/log/mongodb'
        sh 'export PATH=/usr/local/mongodb/mongodbserver/bin:$PATH'
        sh 'mongod --dbpath /var/lib/mongo --logpath /var/log/mongodb/mongod.log --fork'
      }
    }

    stage('Lint with flake8') {
      steps {
        sh 'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics && flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics'
      }
    }

    stage('Test with pytest') {
      steps {
        sh 'pytest'
      }
    }

  }
  environment {
    CODING_DOCKER_REG_HOST = "${CCI_CURRENT_TEAM}-docker.pkg.${CCI_CURRENT_DOMAIN}"
    CODING_DOCKER_IMAGE_NAME = "${PROJECT_NAME.toLowerCase()}/${DOCKER_REPO_NAME}/${DOCKER_IMAGE_NAME}"
  }
}