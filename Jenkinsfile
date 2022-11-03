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
      steps {
        script {
          def remoteConfig = [:]
          remoteConfig.name = "CODING-remote-deploy"
          remoteConfig.host = "${REMOTE_HOST}"
          remoteConfig.port = "${REMOTE_SSH_PORT}".toInteger()
          remoteConfig.allowAnyHosts = true

          withCredentials([
            sshUserPrivateKey(
              credentialsId: "${REMOTE_CRED}",
              keyFileVariable: "/home/ubuntu/.ssh/id_ed25519"
            ),
          ]) {
            // SSH 登录用户名
            remoteConfig.user = "${REMOTE_USER_NAME}"
            remoteConfig.password = "${REMOTE_USER_PASSWORD}"
            // SSH 私钥文件地址
            remoteConfig.identityFile = privateKeyFilePath

            sshCommand(
              remote: remoteConfig,
              command: "bash /home/ubuntu/deploy/deploy.sh",
              sudo: true,
            )

          }
        }
      }
    }
  }
}