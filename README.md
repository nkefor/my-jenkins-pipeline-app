# Node.js CI/CD Pipeline with Ansible

This project demonstrates a Continuous Integration/Continuous Deployment (CI/CD) pipeline for a Node.js application using Ansible for automated deployment.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Project Files](#project-files)
  - [hosts.ini](#hostsini)
  - [deploy_app.yml](#deploy_appyml)
- [CI/CD Workflow](#ci/cd-workflow)
- [How to Use (Manual Test)](#how-to-use-manual-test)
- [Integration with CI Server (e.g., Jenkins)](#integration-with-ci-server-e.g.-jenkins)
- [Contributing](#contributing)
- [License](#license)

## Overview

This setup provides a robust and automated way to deploy a Node.js application. While a CI server (like Jenkins, GitLab CI, or GitHub Actions) handles the integration aspects (building, testing), Ansible takes over for the continuous deployment, ensuring the application is consistently deployed and managed on target servers.

## Architecture

1.  **Source Code Repository:** Your Node.js application code (e.g., GitHub).
2.  **CI Server (e.g., Jenkins):**
    *   Pulls the latest code.
    *   Installs Node.js dependencies.
    *   Runs tests.
    *   **Triggers Ansible Playbook** for deployment.
3.  **Ansible Control Node:** (Can be the CI server itself, or a dedicated machine).
    *   Contains Ansible playbooks and inventory.
    *   Connects to target deployment servers via SSH.
4.  **Target Deployment Servers:**
    *   Where your Node.js application will run.
    *   Ansible will configure these servers and deploy the application.

## Prerequisites

Before you begin, ensure you have the following:

*   **Node.js Application:** Your existing Node.js application files (`server.js`, `package.json`).
*   **Ansible:** Installed on your CI server or a dedicated control node.
*   **SSH Access:** The Ansible control node must have SSH access (key-based authentication is highly recommended) to your target deployment servers.
*   **Target Deployment Servers:** Linux servers where Node.js and `npm` are installed (or Ansible can install them).
*   **CI Server (Optional):** Configured to pull your Git repository and execute shell commands.

## Project Files

### `hosts.ini`

This file defines the inventory of your target deployment servers. Replace the placeholders with your actual server details.

```ini
[webservers]
your_deployment_server_ip ansible_user=your_ssh_user ansible_ssh_private_key_file=/path/to/your/ssh/key
# Add more servers if you have them:
# another_server_ip ansible_user=another_ssh_user ansible_ssh_private_key_file=/path/to/your/ssh/key
```

### `deploy_app.yml`

This is the main Ansible playbook responsible for deploying the Node.js application. It performs the following tasks:

*   Ensures Node.js and npm are installed.
*   Installs `pm2` (a Node.js process manager) globally.
*   Creates the application deployment directory.
*   Clones or updates the application repository from GitHub.
*   Installs Node.js dependencies on the target server.
*   Starts or restarts the Node.js application using `pm2`.
*   Configures `pm2` to start the application on server boot.

```yaml
---
- name: Deploy Node.js Application
  hosts: webservers
  become: yes # Run tasks with sudo privileges
  vars:
    app_name: nodejs-app
    app_path: /opt/{{ app_name }}
    app_port: 3000
    git_repo_url: "https://github.com/nkefor/my-jenkins-pipeline-app.git" # Your GitHub repo URL
    git_branch: main

  tasks:
    - name: Ensure Node.js and npm are installed (Ubuntu/Debian)
      ansible.builtin.apt:
        name:
          - nodejs
          - npm
        state: present
        update_cache: yes
      when: ansible_os_family == "Debian"

    - name: Ensure Node.js and npm are installed (CentOS/RHEL)
      ansible.builtin.yum:
        name:
          - nodejs
          - npm
        state: present
        update_cache: yes
      when: ansible_os_family == "RedHat"

    - name: Install pm2 globally (process manager)
      ansible.builtin.npm:
        name: pm2
        global: yes
        state: present

    - name: Create application directory
      ansible.builtin.file:
        path: "{{ app_path }}"
        state: directory
        mode: '0755'

    - name: Clone or update application repository
      ansible.builtin.git:
        repo: "{{ git_repo_url }}"
        dest: "{{ app_path }}"
        version: "{{ git_branch }}"
        force: yes # Force update to latest commit

    - name: Install Node.js dependencies
      ansible.builtin.npm:
        path: "{{ app_path }}"
        production: yes # Install only production dependencies

    - name: Start/Restart Node.js application with pm2
      ansible.builtin.command: pm2 restart {{ app_name }} || pm2 start {{ app_path }}/server.js --name {{ app_name }} -- -p {{ app_port }}
      args:
        chdir: "{{ app_path }}"
      changed_when: true # Always report as changed to ensure pm2 command runs

    - name: Save pm2 process list
      ansible.builtin.command: pm2 save
      changed_when: true

    - name: Ensure pm2 starts on boot
      ansible.builtin.command: pm2 startup systemd
      changed_when: true
      # This command generates a systemd unit file. You might need to run it once manually
      # on the target server if it fails due to permissions or environment issues.
```

## CI/CD Workflow

1.  **Code Commit:** Developer pushes code changes to the GitHub repository.
2.  **CI Server Trigger:** The CI server (e.g., Jenkins) detects the new commit and triggers a build.
3.  **Build & Test:** The CI server pulls the code, installs Node.js dependencies, and runs tests.
4.  **Ansible Deployment:** Upon successful CI, the CI server executes the `ansible-playbook` command, pointing to `hosts.ini` and `deploy_app.yml`.
5.  **Application Deployment:** Ansible connects to the target servers, performs the deployment tasks (cloning repo, installing dependencies, starting app), and ensures the application is running.

## How to Use (Manual Test)

To test the Ansible playbook manually (without a CI server):

1.  **Ensure Ansible is installed** on your local machine or a dedicated control node.
2.  **Update `hosts.ini`:** Replace `your_deployment_server_ip`, `your_ssh_user`, and `/path/to/your/ssh/key` with your actual server details and the path to your SSH private key.
3.  **Run the playbook:**
    ```bash
    ansible-playbook -i hosts.ini deploy_app.yml
    ```
    This will connect to your specified server, install Node.js/npm/pm2 (if not present), pull your application code, install its dependencies, and start/restart it using pm2.

## Integration with CI Server (e.g., Jenkins)

To integrate this with a CI server, you would typically add a stage in your CI pipeline (e.g., `Jenkinsfile`) to execute the Ansible playbook after successful build and test stages. An example `Jenkinsfile` snippet is provided below:

```groovy
pipeline {
    agent any

    environment {
        // Define your deployment server details here or use Jenkins credentials
        DEPLOY_SERVER_IP = "your_deployment_server_ip"
        SSH_USER = "your_ssh_user"
        SSH_KEY_PATH = "/path/to/your/ssh/key.pem" // Path on the Jenkins server
    }

    stages {
        stage('Checkout') { /* ... */ }
        stage('Install Dependencies (CI Server)') { /* ... */ }
        stage('Run Tests') { /* ... */ }

        stage('Deploy with Ansible') {
            steps {
                echo 'Deploying application using Ansible...'
                // Ensure Ansible is installed on the Jenkins agent
                // and the SSH key is accessible.

                // Create a temporary hosts.ini file for Ansible
                sh """
                    echo "[webservers]" > hosts.ini
                    echo "${DEPLOY_SERVER_IP} ansible_user=${SSH_USER} ansible_ssh_private_key_file=${SSH_KEY_PATH}" >> hosts.ini
                """

                // Run the Ansible playbook
                sh "ansible-playbook -i hosts.ini deploy_app.yml"
            }
        }
    }

    post { /* ... */ }
}
```

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).