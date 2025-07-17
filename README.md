# Server Health and Uptime Monitoring with Prometheus and Grafana

This project outlines the setup of a robust monitoring system using Prometheus for metric collection and Grafana for powerful data visualization. This system is designed to track server health, uptime, and various performance metrics, providing insights into your infrastructure's operational status.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Step-by-Step Configuration](#step-by-step-configuration)
  - [Step 1: Set up Prometheus Server](#step-1-set-up-prometheus-server)
  - [Step 2: Install Node Exporter on Target Servers](#step-2-install-node-exporter-on-target-servers)
  - [Step 3: Set up Grafana](#step-3-set-up-grafana)
  - [Step 4: Configure Grafana Data Source](#step-4-configure-grafana-data-source)
  - [Step 5: Import a Grafana Dashboard](#step-5-import-a-grafana-dashboard)
- [Scaling and Advanced Features](#scaling-and-advanced-features)
- [Contributing](#contributing)
- [License](#license)

## Overview

This monitoring solution provides real-time insights into the performance and availability of your servers. By collecting metrics from various sources and visualizing them in customizable dashboards, you can proactively identify issues, optimize resource utilization, and ensure the continuous health of your infrastructure.

## Architecture

*   **Node Exporter:** A lightweight agent installed on each server to be monitored. It exposes hardware and OS metrics (CPU, memory, disk I/O, network, etc.) via an HTTP endpoint.
*   **Prometheus Server:** The central component that scrapes (pulls) metrics from configured targets (Node Exporters) at regular intervals. It stores these metrics in its time-series database.
*   **Grafana:** A powerful open-source platform for data visualization and analytics. It connects to Prometheus as a data source and allows you to create interactive dashboards to display your server metrics.

```
+-------------------+       +-------------------+       +-------------------+
|  Target Server 1  |       |  Target Server 2  |       |  Target Server N  |
|                   |       |                   |       |                   |
| +---------------+ |       | +---------------+ |       | +---------------+ |
| | Node Exporter | | <-----| | Node Exporter | | <-----| | Node Exporter | |
| +-------^-------+ |       | +-------^-------+ |       | +-------^-------+ |
+---------|---------+       +---------|---------+       +---------|---------+
          |                           |                           |
          | (HTTP/HTTPS - Scrape)     | (HTTP/HTTPS - Scrape)     | (HTTP/HTTPS - Scrape)
          |                           |                           |
          v                           v                           v
+-----------------------------------------------------------------------+
|                           Prometheus Server                           |
| (Scrapes metrics, stores in TSDB, provides PromQL query interface)    |
+-----------------------------------------------------------------------+
          ^
          | (HTTP/HTTPS - Query)
          |
+-----------------------------------------------------------------------+
|                                Grafana                                |
| (Connects to Prometheus, visualizes data, creates dashboards)         |
+-----------------------------------------------------------------------+
```

## Prerequisites

*   **Linux Servers:** At least one server to act as the Prometheus/Grafana host, and one or more target servers to monitor.
*   **SSH Access:** To all servers.
*   **`sudo` privileges:** On all servers for installation.
*   **Firewall Rules:** Ensure necessary ports are open (e.g., 9100 for Node Exporter, 9090 for Prometheus, 3000 for Grafana).

## Step-by-Step Configuration

### Step 1: Set up Prometheus Server

1.  **Choose a server** to host Prometheus and Grafana (your "Monitoring Server").
2.  **Download Prometheus:**
    ```bash
    # On your Monitoring Server
    wget https://github.com/prometheus/prometheus/releases/download/v2.53.0/prometheus-2.53.0.linux-amd64.tar.gz
    tar xvfz prometheus-2.53.0.linux-amd64.tar.gz
    cd prometheus-2.53.0.linux-amd64
    ```
3.  **Create `prometheus.yml` configuration:** This file tells Prometheus what to monitor. Replace `your_target_server_ip_1`, `your_target_server_ip_2`, etc., with the actual IP addresses or hostnames of the servers you want to monitor.

    ```yaml
    # my global config
    global:
      scrape_interval: 15s # Set the scrape interval to every 15 seconds. Default is 1m.
      evaluation_interval: 15s # Evaluate rules every 15 seconds. Default is 1m.

    scrape_configs:
      - job_name: "prometheus"
        static_configs:
          - targets: ["localhost:9090"]

      - job_name: "node_exporter"
        static_configs:
          - targets:
              - "your_target_server_ip_1:9100" # Replace with your first target server's IP/hostname
              - "your_target_server_ip_2:9100" # Replace with your second target server's IP/hostname
              # Add more target servers as needed
    ```
4.  **Start Prometheus:**
    ```bash
    # On your Monitoring Server, from the prometheus-2.53.0.linux-amd64 directory
    ./prometheus --config.file=prometheus.yml &
    ```
    (For production, use `systemd`.)
5.  **Verify Prometheus:** Open your browser and go to `http://<Monitoring_Server_IP>:9090`. Go to "Status" -> "Targets" to see if your Node Exporters are listed.

### Step 2: Install Node Exporter on Target Servers

Repeat these steps on *each* server you want to monitor.

1.  **Download Node Exporter:**
    ```bash
    # On each Target Server
    wget https://github.com/prometheus/node_exporter/releases/download/v1.8.1/node_exporter-1.8.1.linux-amd64.tar.gz
    tar xvfz node_exporter-1.8.1.linux-amd64.tar.gz
    cd node_exporter-1.8.1.linux-amd64
    ```
2.  **Start Node Exporter:**
    ```bash
    # On each Target Server
    ./node_exporter &
    ```
    (For production, use `systemd`.)
3.  **Verify Node Exporter:** Open your browser and go to `http://<Target_Server_IP>:9100/metrics`. You should see a page full of metrics.
4.  **Check Prometheus Targets:** Go back to your Prometheus UI (`http://<Monitoring_Server_IP>:9090/targets`). Your Node Exporter targets should now show as "UP".

### Step 3: Set up Grafana

1.  **Install Grafana:** (On your Monitoring Server, alongside Prometheus)
    *   **Debian/Ubuntu:**
        ```bash
        sudo apt-get install -y apt-transport-https software-properties-common wget
        sudo mkdir -p /etc/apt/keyrings/
        wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
        echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
        sudo apt-get update
        sudo apt-get install grafana
        ```
    *   **CentOS/RHEL:**
        ```bash
        sudo yum install -y grafana
        ```
2.  **Start Grafana:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start grafana-server
    sudo systemctl enable grafana-server
    ```
3.  **Verify Grafana:** Open your browser and go to `http://<Monitoring_Server_IP>:3000`. Default login: `admin` / `admin`.

### Step 4: Configure Grafana Data Source

1.  **Log in to Grafana.**
2.  Click the **gear icon** (Configuration) on the left sidebar -> **Data sources**.
3.  Click **"Add data source"**.
4.  Select **"Prometheus"**.
5.  **HTTP -> URL:** Enter `http://localhost:9090` (since Prometheus is on the same server).
6.  Click **"Save & test"**. You should see "Data source is working".

### Step 5: Import a Grafana Dashboard

1.  Click the **"+" icon** (Create) on the left sidebar -> **Import**.
2.  **Import via grafana.com:** Enter `1860` (Node Exporter Full dashboard ID).
3.  Click **"Load"**.
4.  Select your Prometheus data source.
5.  Click **"Import"**.

You should now see a comprehensive dashboard displaying metrics from all your monitored servers!

## Scaling and Advanced Features

*   **Alerting:** Use Prometheus Alertmanager for notifications (email, Slack, PagerDuty).
*   **Service Discovery:** For dynamic environments, Prometheus can automatically discover targets (EC2, Kubernetes, etc.).
*   **Custom Metrics:** Expose application-specific metrics using Prometheus client libraries.
*   **High Availability:** Run multiple Prometheus instances or use solutions like Thanos/Cortex.
*   **Recording Rules:** Pre-aggregate metrics for faster query performance.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).
