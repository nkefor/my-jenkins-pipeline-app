# CI/CD Pipeline: Train Schedule Application

This project outlines a comprehensive CI/CD pipeline for a Python-based train schedule application, integrating leading DevOps tools to automate the entire software delivery process, from code commit to deployment on Kubernetes, with integrated monitoring and alerting using Splunk.

## Table of Contents

- [Overview](#overview)
- [Architecture Overview](#architecture-overview)
- [Key Components and Tools](#key-components-and-tools)
- [Project Files](#project-files)
  - [Python Application Files](#python-application-files)
  - [Kubernetes Manifests](#kubernetes-manifests)
  - [Ansible Playbook](#ansible-playbook)
  - [Jenkinsfile](#jenkinsfile)
- [Setup and Configuration Steps](#setup-and-configuration-steps)
- [Monitoring and Alerting with Splunk](#monitoring-and-alerting-with-splunk)
- [Contributing](#contributing)
- [License](#license)

## Overview

This pipeline automates the process of:

*   **Application Development:** A simple Python Flask application.
*   **Containerization:** Packaging the application into Docker images.
*   **Continuous Integration:** Building, testing, and pushing Docker images using Jenkins.
*   **Continuous Deployment:** Deploying the application to a Kubernetes cluster using Ansible.
*   **Monitoring & Alerting:** Centralized logging and operational intelligence with Splunk.

## Architecture Overview

```
+---------------------+     +-------------------+     +-------------------+
| Python Application  |     | Jenkins CI/CD     |     | Container Registry|
| Code Repository     |     | (Orchestrator)    |     | (Docker Images)   |
| (e.g., GitHub)      |     |                   |     |                   |
+----------+----------+     +---------+---------+     +---------+---------+
           |                          |                           ^
           | (Code Push)              | (Image Push)              |
           v                          |                           |
+----------+----------+               |                           |
| Webhook/Polling     |               |                           |
+----------+----------+               |                           |
           |                          |                           |
           | (Trigger)                |                           |
           v                          |                           |
+-----------------------------------------------------------------------+
|                                                                       |
|  Jenkins Pipeline (Jenkinsfile)                                       |
|  - Stage 1: Build (Docker Image)                                      |
|  - Stage 2: Test (Python Unit Tests)                                  |
|  - Stage 3: Push (Docker Image to Registry)                           |
|  - Stage 4: Deploy (Ansible to Kubernetes)                            |
|                                                                       |
+-----------------------------------------------------------------------+
           |
           | (Ansible Playbook Execution)
           v
+---------------------+
| Kubernetes Cluster  |
| (Runs Containerized |
| Application)        |
+---------------------+
           |
           | (Logs/Metrics)
           v
+---------------------+
| Splunk              |
| (Monitoring &       |
| Alerting)           |
+---------------------+
```

## Key Components and Tools

*   **Python Application:** A simple Flask application simulating a train schedule service.
*   **Docker:** Containerizes the Python application for consistent deployment.
*   **Jenkins:** The central CI/CD orchestrator. It defines the pipeline stages, automates builds, tests, image pushes, and triggers Ansible for deployment.
*   **Ansible:** Used for declarative deployment to Kubernetes. It applies Kubernetes manifests to the cluster.
*   **Kubernetes:** The container orchestration platform where the application will run.
*   **Splunk:** For centralized log management, monitoring, and alerting on application and infrastructure health.
*   **Container Registry:** (e.g., Docker Hub, ECR, GCR) to store Docker images.

## Project Files

### Python Application Files

*   **`app.py`**: A simple Flask application that provides a train schedule API.
*   **`requirements.txt`**: Lists Python dependencies (`Flask`).
*   **`Dockerfile`**: Defines how to build the Docker image for the Python application.

### Kubernetes Manifests

*   **`k8s-deployment.yml`**: Kubernetes Deployment and Service definitions for the train schedule application. The image tag will be dynamically replaced by Jenkins.

### Ansible Playbook

*   **`ansible-deploy-k8s.yml`**: An Ansible playbook executed by Jenkins to apply the Kubernetes manifests to the cluster using `kubectl`.

### Jenkinsfile

*   **`Jenkinsfile`**: Defines the CI/CD pipeline stages in Groovy syntax, orchestrating the entire workflow.

## Setup and Configuration Steps

1.  **Prerequisites:**
    *   **Kubernetes Cluster:** A running Kubernetes cluster.
    *   **Jenkins Server:** A running Jenkins instance with Docker, Python, and Ansible installed on the agent that will run this pipeline.
    *   **`kubectl`:** Configured on the Jenkins agent with access to your Kubernetes cluster. The `kubeconfig` file should be placed at the path specified in `Jenkinsfile` (`/var/jenkins_home/.kube/config` or similar).
    *   **Container Registry Account:** (e.g., Docker Hub).
    *   **Splunk Instance:** A running Splunk instance with HTTP Event Collector (HEC) enabled if you plan to use the Splunk logging.

2.  **Update Placeholders:**
    *   **`Jenkinsfile`:**
        *   `DOCKER_REGISTRY`: Replace `"your-docker-registry"` with your actual Docker registry (e.g., `"docker.io/your-username"`).
        *   `KUBECONFIG_PATH`: Ensure this path is correct for your Jenkins agent.
        *   **Splunk HEC (in `post` section):** Uncomment and replace `your-splunk-hec-endpoint` and `<token>` with your Splunk HEC details if you want to send deployment logs to Splunk.
    *   **`k8s-deployment.yml`:** The `image` placeholder will be replaced by Jenkins during the deployment stage.

3.  **Jenkins Credentials (if using private registry):**
    *   If your Docker registry is private, you'll need to configure Jenkins credentials (Type: "Username with password") with your Docker registry username and password. Update the `credentialsId` in the `Jenkinsfile`'s "Push Docker Image" stage.

4.  **Jenkins Job Configuration:**
    *   Create a new Jenkins Pipeline job.
    *   Configure it to pull from your Git repository (where these files will be pushed).
    *   Set the "Definition" to "Pipeline script from SCM" and point to the `Jenkinsfile`.

## Monitoring and Alerting with Splunk

*   **Log Collection:**
    *   Configure your Kubernetes cluster to send container logs to Splunk. This can be done using a Splunk Universal Forwarder deployed as a DaemonSet in Kubernetes, or by using a logging agent like Fluentd/Fluent Bit that forwards logs to Splunk HEC.
*   **Metrics Collection:**
    *   Use Splunk Connect for Kubernetes or a Universal Forwarder to collect Kubernetes metrics (e.g., from cAdvisor, Kube-state-metrics) and send them to Splunk.
*   **Alerting:**
    *   In Splunk, create searches and alerts based on:
        *   **Application Logs:** Errors, exceptions, specific messages from your Python app.
        *   **Kubernetes Events:** Pod crashes, deployment failures, OOMKills.
        *   **Performance Metrics:** High CPU/memory usage, low disk space on nodes.
        *   **Deployment Status:** Use the HEC events sent by Jenkins (as commented in `Jenkinsfile`) to alert on successful or failed deployments.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).
