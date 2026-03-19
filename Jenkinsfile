#!/usr/bin/env groovy

pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('fc315f09-b7c1-4e5f-bd8b-b138def434aa')
        DOCKER_IMAGE_NAME = 'arynxd/uws-running-app'
        DOCKER_IMAGE_TAG = "${env.GIT_COMMIT.take(7)}-${env.BUILD_NUMBER}"
        GIT_REPO = 'https://github.com/nullishamy/uws-running-app.git'
        GIT_BRANCH = 'main'
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Verify Trigger') {
            steps {
                script {
                    echo "Build triggered by: ${env.GIT_COMMIT}"
                    echo "Commit message: ${env.GIT_COMMIT_MESSAGE}"
                    echo "Branch: ${env.GIT_BRANCH}"
                    echo "Build number: ${env.BUILD_NUMBER}"
                }
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
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
                        credentialsId: 'fc315f09-b7c1-4e5f-bd8b-b138def434aa',
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
            echo 'Docker image successfully built and pushed to DockerHub!'
        }
        failure {
            echo 'Build or push failed. Check console output for details.'
        }
    }
}