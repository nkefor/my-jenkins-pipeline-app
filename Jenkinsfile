pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = "your-docker-registry" // e.g., "docker.io/your-username"
        DOCKER_IMAGE_NAME = "${DOCKER_REGISTRY}/train-schedule-app"
        KUBECONFIG_PATH = "/var/jenkins_home/.kube/config" // Path to kubeconfig on Jenkins agent
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    // Build the Docker image
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ."
                    // Tag with 'latest' as well
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        stage('Run Python Unit Tests') {
            steps {
                script {
                    echo "Running Python unit tests..."
                    // Run tests inside a temporary container
                    sh "docker run --rm ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} python -m unittest discover"
                    // If you have a dedicated test script, e.g., test_app.py
                    // sh "docker run --rm ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} python test_app.py"
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    echo "Pushing Docker image to registry..."
                    // Authenticate to Docker registry (if private)
                    // withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    //     sh "echo \"$DOCKER_USER\" | docker login -u \"$DOCKER_USER\" --password-stdin ${DOCKER_REGISTRY}"
                    // }
                    sh "docker push ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    sh "docker push ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        stage('Deploy to Kubernetes with Ansible') {
            steps {
                script {
                    echo "Deploying to Kubernetes using Ansible..."
                    // Replace image placeholder in k8s-deployment.yml
                    sh "sed -i 's|your-docker-registry/train-schedule-app:latest|${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}|g' k8s-deployment.yml"

                    // Ensure Ansible is installed on the Jenkins agent
                    // and kubectl is configured with access to the cluster.
                    // The kubeconfig file should be placed at KUBECONFIG_PATH on the Jenkins agent.

                    // Run the Ansible playbook
                    sh "ansible-playbook -i localhost, ansible-deploy-k8s.yml"
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
            cleanWs() // Clean up the workspace
        }
        success {
            echo 'Pipeline executed successfully!'
            // Add Splunk logging for successful deployment
            // sh "curl -k -H 'Authorization: Splunk <token>' -d '{\"event\":{\"message\":\"Train Schedule App deployed successfully!\",\"app_version\":\"${env.BUILD_NUMBER}\",\"status\":\"success\"}}' https://your-splunk-hec-endpoint:8088/services/collector"
        }
        failure {
            echo 'Pipeline failed.'
            // Add Splunk logging for failed deployment
            // sh "curl -k -H 'Authorization: Splunk <token>' -d '{\"event\":{\"message\":\"Train Schedule App deployment failed!\",\"app_version\":\"${env.BUILD_NUMBER}\",\"status\":\"failure\"}}' https://your-splunk-hec-endpoint:8088/services/collector"
        }
    }
}