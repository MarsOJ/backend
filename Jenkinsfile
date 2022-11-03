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
    def remoteConfig = [:]
              remoteConfig.name = "CODING-remote-deploy"
              remoteConfig.host = "${REMOTE_HOST}"
              remoteConfig.user = "${REMOTE_USER_NAME}"
              remoteConfig.password = "${REMOTE_USER_PASSWORD}"
              remoteConfig.allowAnyHosts = true
    stage("Remote Deploy") {
      sshCommand remote: remote, command: "ls"
    }
  }
}