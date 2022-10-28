pipeline {
  agent {
        docker {
            image 'python:3.10' 
            label 'docker-node'
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
        sh 'python -m pip install --upgrade pip && pip install flake8 flake8-bugbear flake8-import-order pytest -i https://pypi.tuna.tsinghua.edu.cn/simple  &&     if [ -f requirements.txt ]; then pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple; fi'
      }
    }

    stage('Lint with flake8') {
      steps {
        sh 'python -m flake8 .'
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