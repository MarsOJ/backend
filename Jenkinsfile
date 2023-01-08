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
        sh 'rm -f mongodb-linux-x86_64-rhel80-5.0.4.tgz'
        sh 'mv /usr/local/mongodb/mongodb-linux-x86_64-rhel80-5.0.4 /usr/local/mongodb/mongodbserver'
        sh 'mkdir -p /var/lib/mongo'
        sh 'mkdir -p /var/log/mongodb'
        sh 'chmod 777 /var/lib/mongo'
        sh 'chmod 777 /var/log/mongodb'
        sh 'ln -sf /usr/local/mongodb/mongodbserver/bin/mongod /usr/bin/mongod&& ln -sf /usr/local/mongodb/mongodbserver/bin/mongo /usr/bin/mongo && ln -sf /usr/local/mongodb/mongodbserver/bin/mongos /usr/bin/mongos'
        sh 'mongod --dbpath /var/lib/mongo --logpath /var/log/mongodb/mongod.log --fork'
        // mongod --dbpath /var/lib/mongodb --logpath /var/log/mongodb/mongod.log --fork
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
}