# Node.js Jenkins CI/CD Pipeline Application

This project demonstrates a complete Continuous Integration/Continuous Deployment (CI/CD) pipeline using Jenkins for a simple Node.js application. The pipeline automates the process of building, testing, containerizing, and deploying the application to a remote server.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development](#local-development)
- [CI/CD Pipeline (Jenkins Setup)](#ci/cd-pipeline-jenkins-setup)
  - [Jenkins Plugins](#jenkins-plugins)
  - [Jenkins Credentials](#jenkins-credentials)
  - [Jenkinsfile Explanation](#jenkinsfile-explanation)
  - [Configuring the Jenkins Job](#configuring-the-jenkins-job)
- [Deployment](#deployment)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

*   **Node.js Application:** A basic Express.js web server.
*   **Dockerization:** Application packaged into a Docker image.
*   **Automated Build & Test:** Jenkins automatically builds and runs tests on every code push.
*   **Docker Image Management:** Built images are pushed to Docker Hub (or a specified container registry).
*   **Automated Deployment:** Application is automatically deployed to a remote server via SSH.
*   **Version Control Integration:** Seamless integration with GitHub.

## Technologies Used

*   **Node.js:** JavaScript runtime for the backend application.
*   **Express.js:** Web framework for Node.js.
*   **Docker:** Containerization platform for packaging the application.
*   **Jenkins:** Automation server for CI/CD pipeline orchestration.
*   **Git:** Version control system.
*   **GitHub:** Code hosting platform.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed and configured:

*   **Node.js and npm:** For local development and testing.
*   **Docker:** For building and running Docker images locally.
*   **Git:** For version control.
*   **Jenkins Server:** A running Jenkins instance with necessary plugins (see [Jenkins Plugins](#jenkins-plugins)).
*   **AWS Account (Optional):** If deploying to AWS EC2.
*   **Deployment Server:** A remote server (e.g., EC2 instance) with Docker installed and accessible via SSH.
*   **Docker Hub Account:** For pushing and pulling Docker images.

### Local Development

To run the Node.js application locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/nkefor/my-jenkins-pipeline-app.git
    cd my-jenkins-pipeline-app
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Start the application:**
    ```bash
    npm start
    ```
    The application will be accessible at `http://localhost:3000`.

## CI/CD Pipeline (Jenkins Setup)

The CI/CD pipeline is defined in the `Jenkinsfile` and orchestrated by Jenkins.

### Jenkins Plugins

Ensure the following Jenkins plugins are installed (`Manage Jenkins` -> `Plugins` -> `Available plugins`):

*   `Pipeline` (usually installed by default)
*   `Git`
*   `NodeJS`
*   `Docker Pipeline`
*   `SSH Agent`

### Jenkins Credentials

You need to configure the following credentials in Jenkins (`Manage Jenkins` -> `Credentials` -> `System` -> `Global credentials (unrestricted)` -> `Add Credentials`):

1.  **Docker Hub Credentials:**
    *   **Kind:** `Username with password`
    *   **Scope:** `Global`
    *   **Username:** Your Docker Hub username
    *   **Password:** Your Docker Hub password
    *   **ID:** `dockerhub-creds` (This ID is referenced in the `Jenkinsfile`)
    *   **Description:** `Docker Hub credentials`

2.  **Deployment Server SSH Key:**
    *   **Kind:** `SSH Username with private key`
    *   **Scope:** `Global`
    *   **ID:** `deploy-server-ssh-key` (This ID is referenced in the `Jenkinsfile`)
    *   **Description:** `SSH key for deployment server`
    *   **Username:** The SSH username for your deployment server (e.g., `ubuntu`, `ec2-user`)
    *   **Private Key:** Select `Enter directly` and paste your private SSH key.

### Jenkinsfile Explanation

The `Jenkinsfile` defines the pipeline stages:

*   **`Checkout`**: Fetches the latest code from the Git repository.
*   **`Install Dependencies`**: Runs `npm install` to set up project dependencies.
*   **`Run Tests`**: Executes `npm test` (currently a placeholder, but can be extended with actual unit tests).
*   **`Build Docker Image`**: Builds the Docker image for the application, tagging it with the Jenkins build number.
*   **`Push Docker Image`**: Pushes the built Docker image to Docker Hub.
*   **`Deploy to Production`**: Connects to the deployment server via SSH, stops/removes the old container, pulls the new image, and runs it.

**Important:** Update the environment variables in your `Jenkinsfile` with your specific details:

```groovy
    environment {
        DOCKERHUB_CREDENTIALS_ID = 'dockerhub-creds'
        DOCKER_IMAGE_NAME        = "your-dockerhub-username/jenkins-nodejs-cicd" // <-- UPDATE THIS
        DEPLOY_SERVER_IP         = "your_deployment_server_ip" // <-- UPDATE THIS
        DEPLOY_SERVER_USER       = "your_deployment_server_user" // <-- UPDATE THIS
        SSH_CREDENTIALS_ID       = 'deploy-server-ssh-key'
    }
```

### Configuring the Jenkins Job

1.  **Create a New Item** in Jenkins (e.g., `my-nodejs-cicd-pipeline`).
2.  Select **"Pipeline"** as the project type.
3.  In the **General** section, optionally link to your GitHub project: `https://github.com/nkefor/my-jenkins-pipeline-app`.
4.  In **Build Triggers**, select **"GitHub hook trigger for GITScm polling"** for automatic builds on push.
5.  In the **Pipeline** section:
    *   **Definition:** `Pipeline script from SCM`
    *   **SCM:** `Git`
    *   **Repository URL:** `https://github.com/nkefor/my-jenkins-pipeline-app.git`
    *   **Credentials:** (Leave blank if public, otherwise select your GitHub credentials)
    *   **Branches to build:** `*/main`
    *   **Script Path:** `Jenkinsfile`
6.  **Save** the job.

## Deployment

Once the Jenkins pipeline runs successfully, the Node.js application will be deployed to your specified `DEPLOY_SERVER_IP` and accessible on port `3000`.

To access the deployed application, open your web browser and navigate to:
`http://<your_deployment_server_ip>:3000`

## Usage

This project serves as a template for setting up a robust CI/CD pipeline for Node.js applications. You can extend it by:

*   Adding comprehensive unit and integration tests.
*   Implementing more sophisticated deployment strategies (e.g., blue/green, canary).
*   Integrating with other tools (e.g., SonarQube for code quality, Slack for notifications).
*   Using a different container registry or cloud provider.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).
