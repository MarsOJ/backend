pipeline {
  agent any
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
        sh '/usr/bin/python -m pip install --upgrade pip  &&   pip3 install flake8 pytest   &&     if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi'
      }
    }

    stage('Lint with flake8') {
      steps {
        sh 'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistic  &&   flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics'
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