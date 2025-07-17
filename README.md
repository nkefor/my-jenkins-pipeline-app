# Automated Patch Management and Software Updates with Ansible

This project provides an Ansible-based solution for automating the process of patch management and software updates across multiple Linux servers. It ensures that your servers are kept up-to-date with the latest security patches and software versions, enhancing security and stability.

## Table of Contents

- [Overview](#overview)
- [How it Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Project Files](#project-files)
  - [hosts.ini](#hostsini)
  - [patch_management.yml](#patch_managementyml)
- [How to Use](#how-to-use)
- [Important Considerations for Production](#important-considerations-for-production)
- [Contributing](#contributing)
- [License](#license)

## Overview

Patch management is a critical aspect of server maintenance, ensuring systems are protected against known vulnerabilities and benefit from performance improvements. This solution leverages Ansible's agentless and idempotent capabilities to streamline this process across diverse Linux environments (Debian/Ubuntu and CentOS/RHEL).

## How it Works

The Ansible playbook performs the following actions on each target server:

1.  **Updates Package Cache:** Refreshes the local package manager's cache (`apt update` or `yum makecache`).
2.  **Upgrades All Packages:** Installs the latest versions of all installed packages (`apt dist-upgrade` or `yum update`).
3.  **Cleans Up (Debian/Ubuntu):** Removes obsolete packages and cleans the local repository of retrieved package files.
4.  **Checks for Reboot Requirement:** Determines if a system reboot is necessary after updates (e.g., by checking for `/var/run/reboot-required` on Debian/Ubuntu or using `needs-restarting` on CentOS/RHEL).
5.  **Performs Conditional Reboot:** If a reboot is required, the playbook initiates a system reboot and waits for the server to come back online.

## Prerequisites

*   **Ansible:** Installed on your control machine (the machine from which you'll run the playbook).
*   **SSH Access:** The Ansible control machine must have SSH access (preferably key-based authentication) to all target servers. The SSH user must have `sudo` privileges on the target servers.
*   **Target Servers:** Linux servers running Debian/Ubuntu or CentOS/RHEL distributions.

## Project Files

### `hosts.ini`

This is your Ansible inventory file, defining the target servers to be patched. Replace the placeholders with your actual server details and SSH key path.

```ini
[linux_servers]
server1.example.com ansible_user=your_ssh_user ansible_ssh_private_key_file=/path/to/your/ssh/key.pem
server2.example.com ansible_user=your_ssh_user ansible_ssh_private_key_file=/path/to/your/ssh/key.pem
# Add more servers as needed
```

### `patch_management.yml`

This is the main Ansible playbook containing the logic for updating and upgrading packages, and handling reboots.

```yaml
---
- name: Automated Patch Management and Software Updates
  hosts: linux_servers
  become: yes # Run tasks with sudo privileges

  vars:
    reboot_required_file: /var/run/reboot-required # Standard file for Debian/Ubuntu
    reboot_marker_file: /tmp/ansible_reboot_marker # Custom marker for Ansible

  tasks:
    - name: Update apt cache (Debian/Ubuntu)
      ansible.builtin.apt:
        update_cache: yes
        cache_valid_time: 3600 # Cache valid for 1 hour
      when: ansible_os_family == "Debian"

    - name: Upgrade all packages (Debian/Ubuntu)
      ansible.builtin.apt:
        upgrade: dist
      when: ansible_os_family == "Debian"

    - name: Update yum cache (CentOS/RHEL)
      ansible.builtin.yum:
        update_cache: yes
      when: ansible_os_family == "RedHat"

    - name: Upgrade all packages (CentOS/RHEL)
      ansible.builtin.yum:
        name: "*"
        state: latest
      when: ansible_os_family == "RedHat"

    - name: Clean up unused packages (Debian/Ubuntu)
      ansible.builtin.apt:
        autoremove: yes
        autoclean: yes
      when: ansible_os_family == "Debian"

    - name: Check if reboot is required (Debian/Ubuntu)
      ansible.builtin.stat:
        path: "{{ reboot_required_file }}"
      register: reboot_required_check_debian
      when: ansible_os_family == "Debian"

    - name: Check if reboot is required (CentOS/RHEL - using needs-restarting)
      ansible.builtin.command: needs-restarting -r
      register: reboot_required_check_rhel
      changed_when: false # This command doesn't change system state
      failed_when: reboot_required_check_rhel.rc not in [0, 1] # 0=no reboot, 1=reboot needed
      when: ansible_os_family == "RedHat"

    - name: Create reboot marker file if reboot is required (Debian/Ubuntu)
      ansible.builtin.file:
        path: "{{ reboot_marker_file }}"
        state: touch
      when:
        - ansible_os_family == "Debian"
        - reboot_required_check_debian.stat.exists

    - name: Create reboot marker file if reboot is required (CentOS/RHEL)
      ansible.builtin.file:
        path: "{{ reboot_marker_file }}"
        state: touch
      when:
        - ansible_os_family == "RedHat"
        - reboot_required_check_rhel.rc == 1 # needs-restarting returns 1 if reboot is needed

  handlers:
    - name: Perform reboot if marker file exists
      ansible.builtin.reboot:
        reboot_timeout: 600 # Wait up to 10 minutes for reboot
      when:
        - ansible.builtin.stat(path=reboot_marker_file).stat.exists
      # This handler will only run if explicitly notified or if the playbook finishes
      # and the marker file exists. For a full reboot strategy, you might
      # want to run this as a separate play or use a more sophisticated approach.

- name: Trigger Reboot if necessary
  hosts: linux_servers
  become: yes
  tasks:
    - name: Check for reboot marker file
      ansible.builtin.stat:
        path: "{{ hostvars[inventory_hostname].reboot_marker_file }}"
      register: final_reboot_check

    - name: Perform reboot if marker file exists and remove it
      ansible.builtin.reboot:
        reboot_timeout: 600
      when: final_reboot_check.stat.exists
      notify: Remove reboot marker file

  handlers:
    - name: Remove reboot marker file
      ansible.builtin.file:
        path: "{{ hostvars[inventory_hostname].reboot_marker_file }}"
        state: absent
```

## How to Use

1.  **Update `hosts.ini`:**
    *   Replace `server1.example.com`, `server2.example.com` with the actual hostnames or IP addresses of your Linux servers.
    *   Replace `your_ssh_user` with the SSH username that has `sudo` privileges on those servers.
    *   Replace `/path/to/your/ssh/key.pem` with the absolute path to your SSH private key on the Ansible control machine.
2.  **Run the Playbook:**
    ```bash
    ansible-playbook -i hosts.ini patch_management.yml
    ```

## Important Considerations for Production

*   **Scheduling:** Do not run this playbook randomly in production. Schedule it during maintenance windows using `cron` or a CI/CD pipeline (e.g., Jenkins, GitLab CI).
*   **Testing:** Always test patch management playbooks in a staging environment that mirrors production before applying them to live servers.
*   **Reboot Strategy:** The playbook includes a basic reboot mechanism. For production, you might need a more sophisticated strategy:
    *   **Staggered Reboots:** Reboot servers in batches to maintain service availability.
    *   **Service Checks:** Ensure critical services are up and running after a reboot before proceeding to the next batch.
    *   **Maintenance Windows:** Clearly define and adhere to maintenance windows.
*   **Backup:** Ensure you have proper backups of your servers before performing major updates.
*   **Monitoring:** Monitor the patching process and the health of servers after updates.
*   **Rollback Plan:** Have a plan to roll back if an update causes issues.
*   **Specific Updates:** If you only want to update specific packages, modify the `apt` or `yum` tasks accordingly (e.g., `name: "nginx"` instead of `name: "*"`).
*   **Windows Servers:** This playbook is specifically for Linux. For Windows servers, you would use different Ansible modules (e.g., `win_updates`, `win_reboot`) and connect via WinRM.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).
