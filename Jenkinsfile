#!/usr/bin/env groovy

pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials')
        DOCKER_IMAGE_NAME = 'arynxd/uws-running-app'
        DOCKER_IMAGE_TAG = "${env.BUILD_NUMBER}"
        GIT_REPO = 'https://github.com/nullishamy/uws-running-app.git'
        GIT_BRANCH = 'main'
    }

    triggers {
        githubPush()
    }

    options {
        gitHubBranchProperty(
            branch: GIT_BRANCH,
            triggerOnPush: true,
            triggerAlsoOnMerge: false
        )
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "Checking out source code from ${GIT_REPO}"
                    git(
                        url: GIT_REPO,
                        branch: GIT_BRANCH,
                        changelog: true,
                        poll: false
                    )
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
                    docker.build("${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}", ".")
                }
            }
        }

        stage('Login to DockerHub') {
            steps {
                script {
                    echo "Logging in to DockerHub"
                    withCredentials([usernamePassword(
                        credentialsId: 'docker-hub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )]) {
                        sh 'echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin'
                    }
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                script {
                    echo "Pushing Docker image to registry"
                    sh """
                        docker push ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
                        docker tag ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} ${DOCKER_IMAGE_NAME}:latest
                        docker push ${DOCKER_IMAGE_NAME}:latest
                    """
                }
            }
        }
    }

    post {
        always {
            script {
                echo "Cleaning up workspace"
                sh 'docker logout'
                cleanWs()
            }
        }
        success {
            echo 'Docker image successfully built and pushed to DockerHub'
        }
        failure {
            echo 'Build or push failed. Check console output for details.'
        }
    }
}