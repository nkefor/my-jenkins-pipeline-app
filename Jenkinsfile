
pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS_ID = 'dockerhub-creds'
        DOCKER_IMAGE_NAME        = "your-dockerhub-username/jenkins-nodejs-cicd"
        DEPLOY_SERVER_IP         = "your_deployment_server_ip"
        DEPLOY_SERVER_USER       = "your_deployment_server_user" // e.g., 'ubuntu', 'ec2-user'
        SSH_CREDENTIALS_ID       = 'deploy-server-ssh-key'
    }

    tools {
        // Make sure you have a NodeJS installation configured in
        // Manage Jenkins -> Global Tool Configuration
        nodejs 'NodeJS-14'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                // This will automatically check out the code from the repository
                // that this Jenkins job is configured to use.
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Node.js dependencies...'
                sh 'npm install'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                // Replace with your actual test command if you have one
                sh 'npm test'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${env.DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                withDockerRegistry(credentialsId: env.DOCKERHUB_CREDENTIALS_ID) {
                    sh "docker build -t ${env.DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                echo "Pushing Docker image to Docker Hub..."
                withDockerRegistry(credentialsId: env.DOCKERHUB_CREDENTIALS_ID) {
                    sh "docker push ${env.DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                }
            }
        }

        stage('Deploy to Production') {
            steps {
                echo "Deploying to production server..."
                sshagent(credentials: [env.SSH_CREDENTIALS_ID]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${env.DEPLOY_SERVER_USER}@${env.DEPLOY_SERVER_IP} << 'EOF'
                            # Stop and remove the old container if it exists
                            docker stop nodejs-app || true
                            docker rm nodejs-app || true

                            # Pull the new image
                            docker pull ${env.DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}

                            # Run the new container
                            docker run -d --name nodejs-app -p 3000:3000 ${env.DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}
                        EOF
                    """
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
            // Clean up the workspace to save disk space
            cleanWs()
        }
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
