# Real-time Log Monitor for Security Events

This project provides a simplified Python script for real-time log monitoring, designed to identify possible security breaches by continuously tailing a log file and matching entries against predefined suspicious patterns.

## Table of Contents

- [Overview](#overview)
- [How it Works](#how-it-works)
- [Features](#features)
- [Limitations](#limitations)
- [How to Use](#how-to-use)
- [Example Security Patterns](#example-security-patterns)
- [Next Steps for a Real System](#next-steps-for-a-real-system)
- [Contributing](#contributing)
- [License](#license)

## Overview

This script serves as a proof-of-concept for real-time log analysis, focusing on security-related events. It demonstrates the fundamental principles of continuously monitoring log files and alerting on patterns indicative of suspicious activity, such as failed login attempts, privilege escalation, or unusual command executions.

## How it Works

1.  **Log Tailing:** The script continuously reads new lines appended to a specified log file.
2.  **Pattern Matching:** Each new log entry is checked against a set of predefined regular expressions (regex) that represent known suspicious activities.
3.  **Alerting:** When a match is found, an alert message is printed to the console, highlighting the type of security event and the log entry that triggered it.

## Features

*   Real-time log file monitoring.
*   Identification of common security-related patterns.
*   Categorization of alerts by severity (CRITICAL, HIGH, MEDIUM, LOW).
*   Color-coded console output for easy visibility of alerts.

## Limitations

This script is a simplified example and has several limitations compared to a production-grade security monitoring system:

*   **Basic Pattern Matching:** Uses simple regex; lacks advanced correlation, anomaly detection, or machine learning capabilities.
*   **Log Rotation:** Does not handle log file rotation (when log files are archived and new ones created).
*   **Alerting:** Alerts are only printed to the console; no integration with external notification systems (email, Slack, PagerDuty).
*   **Persistence:** No historical data storage or analysis.
*   **Performance:** May not be suitable for very high-volume log streams.
*   **Windows Event Logs:** Designed for text-based log files common on Linux/Unix systems. Windows Event Logs require different collection methods.
*   **False Positives/Negatives:** Patterns are basic and may lead to false positives or miss subtle threats.

## How to Use

1.  **Choose a Log File:** Identify a log file on your system that contains relevant security events. Common examples on Linux include:
    *   `/var/log/auth.log` (Ubuntu/Debian - authentication logs)
    *   `/var/log/secure` (CentOS/RHEL - authentication logs)
    *   `/var/log/syslog` (General system logs)
    *   `/var/log/kern.log` (Kernel logs)

2.  **Run the Script:** Open your terminal and execute the script, providing the path to the log file you want to monitor:

    ```bash
    python log_monitor.py /var/log/auth.log
    ```
    (Replace `/var/log/auth.log` with the actual path to your log file.)

3.  **Generate Test Events:** While the script is running, try to generate some events that match the patterns to see the alerts:
    *   **Failed Login:** Try to SSH into your server with incorrect credentials multiple times.
    *   **Sudo to Shell:** Run `sudo /bin/bash` or `sudo /bin/sh`.
    *   **User/Group Mod:** Try `sudo useradd testuser` or `sudo groupadd testgroup`.

4.  **Stop Monitoring:** Press `Ctrl+C` to stop the script.

## Example Security Patterns

The script includes predefined patterns for:

*   Failed login attempts (`authentication failure|failed password`)
*   Suspicious `sudo` to shell commands (`sudo: .*COMMAND=\/bin\/(bash|sh)`)
*   User/Group modifications (`useradd|usermod|groupadd|groupmod`)
*   Root SSH sessions (`sshd: session opened for user root`)
*   Potentially destructive or privilege-changing commands (`rm -rf|chmod 777|chown root`)
*   Root CRON job executions (`CRON \(root\) CMD`)

## Next Steps for a Real System

For a production-grade security monitoring solution, consider using:

*   **Log Aggregation Tools:** ELK Stack (Elasticsearch, Logstash, Kibana), Splunk, Datadog, Graylog to centralize logs.
*   **Security Information and Event Management (SIEM) Systems:** Splunk ES, IBM QRadar, Microsoft Sentinel, ArcSight for advanced threat detection, correlation, and incident response.
*   **Endpoint Detection and Response (EDR) Solutions:** For deeper insights into endpoint activity.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).
