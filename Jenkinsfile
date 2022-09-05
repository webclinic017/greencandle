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
                    sh 'image_id=$BUILD_ID docker-compose -f install/docker-compose_unit.yml -p $BUILD_ID build'
                }
            }
        }

        stage("run unittests") {
            steps {
                parallel(
                    "docker_mysql": {
                        echo "testing docker_mysql"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "docker_mysql"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "run1": {
                        echo "testing run1"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "run1"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "run2": {
                        echo "testing run2"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "run2"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "run3": {
                        echo "testing run3"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "run3"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "assocs": {
                        echo "testing assocs"
                        ansiColor('vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "assocs"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]

                        }
                    },
                    "mysql": {
                        echo "testing mysql"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "mysql"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "redis": {
                        echo "testing redis"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "redis"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "docker_redis": {
                        echo "testing docker_redis"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "docker_redis"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "docker_cron": {
                        echo "testing docker_cron"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "docker_cron"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "docker_api": {
                        echo "testing docker_api"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "docker_api"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "stop": {
                        echo "testing stop"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "stop"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "draw": {
                        echo "testing draw"
                        ansiColor('Vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "draw"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "pairs": {
                        echo "testing pairs"
                        ansiColor('vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "pairs"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]

                        }
                    },
                    "scripts": {
                        echo "testing scripts"
                        ansiColor('vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "scripts"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]

                        }
                    },
                    "lint": {
                        echo "testing lint"
                        ansiColor('vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "lint"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]

                        }
                    },
                    "config": {
                        echo "testing config"
                        ansiColor('vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "config"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]

                        }
                    },
                    "borrowed": {
                        echo "testing borrow"
                        ansiColor('vga') {
                            build job: 'unit-tests', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'test', value: "borrowed"),
                                string(name: 'commit', value: env.GIT_COMMIT),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]

                        }
                    }
                )
            }
        }

        stage("Push to registry") {
            steps {
                parallel(
                    "greencandle": {
                        ansiColor('vga') {
                            build job: 'docker-build', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'app', value: "greencandle"),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "mysql": {
                        ansiColor('vga') {
                            build job: 'docker-build', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'app', value: "gc-mysql"),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "redis": {
                        ansiColor('vga') {
                            build job: 'docker-build', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'app', value: "gc-redis"),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "web": {
                        ansiColor('vga') {
                            build job: 'docker-build', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'app', value: "webserver"),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    },
                    "alert": {
                        ansiColor('vga') {
                            build job: 'docker-build', parameters: [string(name: 'version', value: env.GIT_BRANCH),
                                string(name: 'app', value: "alert"),
                                string(name: 'image_id', value: env.BUILD_ID)
                            ]
                        }
                    }
                )
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
