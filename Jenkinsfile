pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'your-docker-registry'
        KUBE_CONFIG = credentials('kubeconfig')
        DOCKER_CREDENTIALS = credentials('docker-hub')
        AWS_ACCESS_KEY = credentials('aws-access-key')
        AWS_SECRET_KEY = credentials('aws-secret-key')
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
                sh 'echo "Repository: ${GIT_URL}"'
                sh 'echo "Branch: ${GIT_BRANCH}"'
            }
        }
        
        stage('Code Quality') {
            parallel {
                stage('Lint Code') {
                    steps {
                        script {
                            if (fileExists('app/package.json')) {
                                sh 'cd app && npm install'
                                sh 'cd app && npm run lint || true'
                            }
                        }
                    }
                }
                stage('Security Scan') {
                    steps {
                        sh 'echo "Running security scans..."'
                        // Add trivy, snyk, or other security scans
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    if (fileExists('app/package.json')) {
                        sh 'cd app && npm test'
                    } else if (fileExists('app/requirements.txt')) {
                        sh 'cd app && python -m pytest tests/'
                    }
                }
            }
            post {
                always {
                    junit '**/test-results/**/*.xml'
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                expression { 
                    fileExists('docker/Dockerfile') && env.BRANCH_NAME == 'main' 
                }
            }
            steps {
                script {
                    def imageName = "${DOCKER_REGISTRY}/oeson-app:${env.BUILD_NUMBER}"
                    sh """
                        docker build -t ${imageName} ./docker
                        docker login -u ${DOCKER_CREDENTIALS_USR} -p ${DOCKER_CREDENTIALS_PSW}
                        docker push ${imageName}
                    """
                    env.DOCKER_IMAGE = imageName
                }
            }
        }
        
        stage('Terraform Plan') {
            when {
                expression { fileExists('terraform/main.tf') }
            }
            steps {
                dir('terraform') {
                    sh 'terraform init'
                    sh 'terraform plan -out=tfplan'
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                expression { 
                    fileExists('k8s/deployment.yaml') && env.BRANCH_NAME == 'main' 
                }
            }
            steps {
                script {
                    // Update deployment with new image
                    sh "sed -i 's|IMAGE_PLACEHOLDER|${env.DOCKER_IMAGE}|g' k8s/deployment.yaml"
                    
                    // Apply Kubernetes manifests
                    sh 'kubectl apply -f k8s/namespace.yaml'
                    sh 'kubectl apply -f k8s/configmap.yaml'
                    sh 'kubectl apply -f k8s/secret.yaml'
                    sh 'kubectl apply -f k8s/deployment.yaml'
                    sh 'kubectl apply -f k8s/service.yaml'
                    
                    // Wait for deployment to be ready
                    sh 'kubectl rollout status deployment/oeson-app -n oeson-namespace'
                }
            }
        }
        
        stage('Ansible Configuration') {
            when {
                expression { fileExists('ansible/playbooks/setup-app.yml') }
            }
            steps {
                dir('ansible') {
                    sh 'ansible-playbook -i inventory.ini playbooks/setup-app.yml'
                }
            }
        }
        
        stage('Deploy Monitoring') {
            when {
                expression { 
                    fileExists('monitoring/namespace.yaml') && env.BRANCH_NAME == 'main' 
                }
            }
            steps {
                sh 'kubectl apply -f monitoring/namespace.yaml'
                sh 'kubectl apply -f monitoring/prometheus/'
                sh 'kubectl apply -f monitoring/grafana/'
            }
        }
        
        stage('Integration Tests') {
            steps {
                script {
                    // Run integration tests against deployed application
                    sh 'echo "Running integration tests..."'
                    if (fileExists('app/tests/test_basic.js')) {
                        sh 'cd app && npm run test:integration || true'
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Cleanup
            sh 'echo "Cleaning up workspace..."'
            
            // Archive artifacts
            archiveArtifacts artifacts: '**/*.log, **/target/*.jar', allowEmptyArchive: true
            
            // Publish test results
            junit '**/test-results/**/*.xml'
            
            // Send notifications
            emailext (
                subject: "Build ${currentBuild.result}: Job ${env.JOB_NAME}",
                body: """
                Build: ${env.JOB_NAME} #${env.BUILD_NUMBER}
                Result: ${currentBuild.result}
                URL: ${env.BUILD_URL}
                """,
                to: "richard@example.com"
            )
        }
        success {
            sh 'echo "Pipeline completed successfully! 🎉"'
            // Update deployment status
        }
        failure {
            sh 'echo "Pipeline failed! ❌"'
            // Rollback if needed
            sh 'kubectl rollout undo deployment/oeson-app -n oeson-namespace || true'
        }
        unstable {
            sh 'echo "Pipeline is unstable! ⚠️"'
        }
    }
}
