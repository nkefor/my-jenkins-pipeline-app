# Ansible Playbook: Configure Web Servers on AWS EC2

This project provides an Ansible playbook to automate the configuration of Nginx web servers on multiple Amazon EC2 instances. It streamlines the process of installing Nginx, ensuring its service is running, and deploying a custom `index.html` page.

## Table of Contents

- [Overview](#overview)
- [How it Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Project Files](#project-files)
  - [hosts.ini](#hostsini)
  - [configure_webservers.yml](#configure_webserversyml)
- [How to Use](#how-to-use)
- [Contributing](#contributing)
- [License](#license)

## Overview

Automating web server setup is crucial for efficient infrastructure management. This Ansible playbook simplifies the deployment of Nginx on diverse Linux distributions running on AWS EC2, ensuring consistency and reducing manual configuration errors.

## How it Works

The Ansible playbook performs the following actions on each target EC2 instance:

1.  **Detects OS:** Identifies whether the instance is Debian-based (e.g., Ubuntu) or RedHat-based (e.g., CentOS, Amazon Linux).
2.  **Updates Package Cache:** Refreshes the package manager's cache (`apt update` or `yum makecache`).
3.  **Installs Nginx:** Installs the Nginx web server package using the appropriate package manager.
4.  **Manages Service:** Ensures the Nginx service is started and configured to run on system boot.
5.  **Deploys `index.html`:** Copies a custom `index.html` file to the Nginx web root, including dynamic information about the instance.

## Prerequisites

*   **Ansible:** Installed on your control machine (the machine from which you'll run the playbook).
*   **AWS EC2 Instances:** Running EC2 instances in AWS that are accessible via SSH.
*   **SSH Access:** The Ansible control machine must have SSH access (preferably key-based authentication) to the EC2 instances. The SSH user must have `sudo` privileges on the target instances.
*   **Security Groups:** Ensure the security groups for your EC2 instances allow:
    *   Inbound SSH (port 22) from your Ansible control machine's IP.
    *   Inbound HTTP (port 80) from the internet (or specific IPs) so you can access the web server.

## Project Files

### `hosts.ini`

This is your Ansible inventory file, defining the target EC2 instances to be configured. Replace the placeholders with your actual server details and SSH key path.

```ini
[ec2_webservers]
ec2-instance-ip-1 ansible_user=your_ssh_user ansible_ssh_private_key_file=/path/to/your/ssh/key.pem
ec2-instance-ip-2 ansible_user=your_ssh_user ansible_ssh_private_key_file=/path/to/your/ssh/key.pem
# Add more EC2 instance IPs/hostnames as needed
```

### `configure_webservers.yml`

This is the main Ansible playbook containing the logic for installing and configuring Nginx.

```yaml
---
- name: Configure Nginx Web Servers on EC2
  hosts: ec2_webservers
  become: yes # Run tasks with sudo privileges

  tasks:
    - name: Update apt cache (Debian/Ubuntu)
      ansible.builtin.apt:
        update_cache: yes
        cache_valid_time: 3600 # Cache valid for 1 hour
      when: ansible_os_family == "Debian"

    - name: Install Nginx (Debian/Ubuntu)
      ansible.builtin.apt:
        name: nginx
        state: present
      when: ansible_os_family == "Debian"

    - name: Update yum cache (CentOS/RHEL/Amazon Linux)
      ansible.builtin.yum:
        update_cache: yes
      when: ansible_os_family == "RedHat"

    - name: Install Nginx (CentOS/RHEL/Amazon Linux)
      ansible.builtin.yum:
        name: nginx
        state: present
      when: ansible_os_family == "RedHat"

    - name: Ensure Nginx service is running and enabled
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: yes

    - name: Deploy custom index.html
      ansible.builtin.copy:
        content: |
          <!DOCTYPE html>
          <html>
          <head>
              <title>Welcome to Nginx on EC2!</title>
              <style>
                  body { font-family: Arial, sans-serif; background-color: #f0f0f0; text-align: center; padding-top: 50px; }
                  h1 { color: #333; }
                  p { color: #666; }
              </style>
          </head>
          <body>
              <h1>Hello from EC2 Web Server!</h1>
              <p>This page was deployed and configured by Ansible.</p>
              <p>Instance IP: {{ ansible_default_ipv4.address }}</p>
              <p>Hostname: {{ ansible_hostname }}</p>
          </body>
          </html>
        dest: /var/www/html/index.html # Default Nginx web root for Debian/Ubuntu
        mode: '0644'
      notify: Restart Nginx

  handlers:
    - name: Restart Nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

## How to Use

1.  **Prepare EC2 Instances:**
    *   Launch your EC2 instances.
    *   Ensure they have a public IP or are accessible from your Ansible control machine.
    *   Attach a security group that allows inbound SSH (port 22) from your control machine and inbound HTTP (port 80) from the internet (or your desired source).
    *   Note down their Public IPs or DNS names and the SSH username (e.g., `ubuntu` for Ubuntu AMIs, `ec2-user` for Amazon Linux/RHEL AMIs).
2.  **Update `hosts.ini`:**
    *   Replace `ec2-instance-ip-1`, `ec2-instance-ip-2` with the actual Public IPs or DNS names of your EC2 instances.
    *   Replace `your_ssh_user` with the correct SSH username for your AMI.
    *   Replace `/path/to/your/ssh/key.pem` with the absolute path to your SSH private key on the Ansible control machine.
3.  **Run the Playbook:**
    Open your terminal in the directory where `hosts.ini` and `configure_webservers.yml` are located and run the playbook:

    ```bash
    ansible-playbook -i hosts.ini configure_webservers.yml
    ```
4.  **Verify:**
    *   After the playbook completes, open a web browser and navigate to the Public IP or Public DNS of your EC2 instances.
    *   You should see a page displaying "Hello from EC2 Web Server!" along with the instance's IP and hostname.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).
