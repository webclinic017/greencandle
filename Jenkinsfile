pipeline {

    agent any
    environment {
        PATH = "/home/jenkins/.local/bin:${env.PATH}"
        DOCKER_HOST = "unix:///var/run/docker.sock"
        image_id = "${env.BUILD_ID}"
        GIT_REPO_NAME = env.GIT_URL.replaceFirst(/^.*?(?::\/\/.*?\/|:)(.*).git$/, '$1')
        SHORT_COMMIT = "${GIT_COMMIT[0..7]}"
    }

    options { disableConcurrentBuilds() }

    stages {
        stage("build docker images") {
            steps {
                sh "env"
                echo 'building apps'
                sh "sudo ln -s . /srv/greencandle"
                ansiColor('vga') {
                    sh 'ls'
                    sh 'docker-compose -f install/docker-compose_jenkins.yml -p $BUILD_ID build --build-arg BRANCH=$GIT_BRANCH --build-arg COMMIT=$SHORT_COMMIT --build-arg DATE="$(date)"'
                }
            }
        }
        stage("run tests") {
            steps {
                echo "run all tests"
                ansiColor('vga') {
                    build job: 'all-tests', parameters:
                    [string(name: 'version', value: env.GIT_BRANCH),
                     string(name: 'image_id', value: env.BUILD_ID)
                     ]
                }
            }
        }

        stage("Push to registry") {
            steps {
                echo "pushing all"
                ansiColor('vga') {
                    build job 'all-push', parameters:
                    [string(name: 'version', value: env.GIT_BRANCH),
                     #string(name: 'app', value: "greencandle"),
                     string(name: 'image_id', value: env.BUILD_ID)
                     ]
                    }
            }
        }
    }

    post {
        success {
            slackSend color: "good", message: "Repo: ${env.GIT_REPO_NAME}\nResult: ${currentBuild.currentResult}\nCommit: ${SHORT_COMMIT}\nBranch: ${env.GIT_BRANCH}\nExecution time: ${currentBuild.durationString.replace(' and counting', '')}\nURL: (<${env.BUILD_URL}|Open>)"
            sh 'docker-compose -f install/docker-compose_jenkins.yml -p $BUILD_ID down --rmi all'
            sh 'docker network prune -f'
        }
        failure { slackSend color: "danger", message: "Repo: ${env.GIT_REPO_NAME}\nResult: ${currentBuild.currentResult}\nCommit: ${SHORT_COMMIT}\nBranch: ${env.GIT_BRANCH}\nExecution time: ${currentBuild.durationString.replace(' and counting', '')}\nURL: (<${env.BUILD_URL}|Open>)"
        }
    }
}
