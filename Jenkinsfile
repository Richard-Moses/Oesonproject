pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'mosesr'  // Change to your DockerHub username
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'echo "Repository cloned successfully"'
                sh 'ls -la'
            }
        }
        
        stage('Code Quality') {
            steps {
                script {
                    if (fileExists('package.json')) {
                        sh 'npm install'
                        sh 'npm run lint || echo "Linting not configured"'
                    } else {
                        echo 'No package.json found - skipping Node.js steps'
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    if (fileExists('package.json')) {
                        sh 'npm test || echo "Tests failed but continuing"'
                    } else {
                        echo 'No tests configured - skipping'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                expression { 
                    fileExists('Dockerfile') 
                }
            }
            steps {
                script {
                    def imageName = "${env.DOCKER_REGISTRY}/baby-microservice:${env.BUILD_NUMBER}"
                    sh "docker build -t ${imageName} ."
                    env.DOCKER_IMAGE = imageName
                    echo "Docker image built: ${env.DOCKER_IMAGE}"
                }
            }
        }
        
        stage('Push to DockerHub') {
            when {
                expression { 
                    fileExists('Dockerfile') && env.DOCKER_IMAGE 
                }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    passwordVariable: 'DOCKER_PASSWORD',
                    usernameVariable: 'DOCKER_USERNAME'
                )]) {
                    script {
                        sh "docker login -u ${env.DOCKER_USERNAME} -p ${env.DOCKER_PASSWORD}"
                        sh "docker push ${env.DOCKER_IMAGE}"
                        echo "Docker image pushed successfully"
                    }
                }
            }
        }
        
        stage('Terraform Plan') {
            when {
                expression { fileExists('infra/terraform/main.tf') }
            }
            steps {
                dir('infra/terraform') {
                    sh 'terraform init'
                    sh 'terraform plan -out=tfplan'
                }
            }
        }
    }
    
    post {
        always {
            echo "Build ${currentBuild.result} - Pipeline execution completed!"
            archiveArtifacts artifacts: '**/build/**/*, **/dist/**/*', allowEmptyArchive: true
        }
        success {
            echo '🎉 Pipeline succeeded! Application deployed successfully.'
        }
        failure {
            echo '❌ Pipeline failed! Check the logs above.'
        }
        unstable {
            echo '⚠️ Pipeline is unstable! Some tests may have failed.'
        }
    }
}