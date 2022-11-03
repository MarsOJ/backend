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
    stage("Remote Deploy") {
      environment {
                BITBUCKET_COMMON_CREDS = credentials('admin:123456')
      }
      steps{
    
        sh "ssh ubuntu@82.157.17.219 && ls"
      }
    }
  }
}