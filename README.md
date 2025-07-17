# AWS CloudWatch Monitoring and Alerting Script

This Python script automates the setup of CloudWatch Alarms for common AWS services (EC2, Application Load Balancer, RDS) and configures Amazon SNS for sending alerts. It provides a foundational approach to monitoring the health and performance of your cloud-based applications on AWS.

## Table of Contents

- [Overview](#overview)
- [How it Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Script Usage](#script-usage)
- [What the Script Does](#what-the-script-does)
- [Contributing](#contributing)
- [License](#license)

## Overview

Effective monitoring is crucial for maintaining the reliability and performance of cloud applications. This script simplifies the process of creating essential CloudWatch alarms that trigger notifications via SNS when predefined metric thresholds are breached. This allows for proactive identification and resolution of potential issues.

## How it Works

The script leverages the `boto3` AWS SDK for Python to interact with AWS services. It performs the following actions:

1.  **SNS Topic Creation:** Creates a new Amazon SNS topic to serve as the notification channel for alarms.
2.  **Email Subscription:** Subscribes a specified email address to the newly created SNS topic.
3.  **CloudWatch Alarm Configuration:** For each specified AWS resource (EC2 instances, ALBs, RDS instances), it creates a set of predefined CloudWatch alarms based on critical health metrics.
4.  **Alerting:** When an alarm's metric crosses its threshold, CloudWatch sends a notification to the SNS topic, which then delivers an email alert to the subscribed address.

## Prerequisites

1.  **AWS Account:** You need an active AWS account.
2.  **AWS CLI Configured:** Install the [AWS CLI](https://aws.amazon.com/cli/) and configure it with your credentials by running `aws configure`. Ensure your AWS credentials have sufficient permissions to create SNS topics and CloudWatch alarms (e.g., `sns:Publish`, `sns:Subscribe`, `sns:CreateTopic`, `cloudwatch:PutMetricAlarm`).
3.  **`boto3`:** Install the AWS SDK for Python.
    ```bash
    pip install boto3
    ```

## Script Usage

Open your terminal in the directory where `aws_cloudwatch_monitor.py` is located and run the script with the required arguments.

**Basic Usage (EC2 CPU Monitoring):**

```bash
python aws_cloudwatch_monitor.py --region us-east-1 --email your-email@example.com --ec2-instance-ids i-0abcdef1234567890
```

**Monitoring Multiple Services:**

```bash
python aws_cloudwatch_monitor.py \
  --region us-east-1 \
  --email your-email@example.com \
  --ec2-instance-ids i-0abcdef1234567890 i-0fedcba9876543210 \
  --alb-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/abcdef1234567890 \
  --rds-instance-ids my-prod-db my-dev-db
```

**Explanation of Arguments:**

*   `--region`: Your AWS region (e.g., `us-east-1`). **Required.**
*   `--email`: The email address where you want to receive SNS notifications. **Required.** You must confirm the subscription in your email inbox after running the script.
*   `--sns-topic-name`: (Optional) A custom name for the SNS topic (default: `ApplicationHealthAlerts`).
*   `--ec2-instance-ids`: (Optional) Space-separated list of EC2 instance IDs to monitor.
*   `--alb-arns`: (Optional) Space-separated list of Application Load Balancer ARNs to monitor.
*   `--rds-instance-ids`: (Optional) Space-separated list of RDS DB instance identifiers to monitor.

## What the Script Does

### SNS Topic Creation

*   Creates an SNS topic named `ApplicationHealthAlerts` (or custom name).
*   Subscribes the provided email address to this topic. **Confirmation via email is required.**

### CloudWatch Alarms Created

**For EC2 Instances:**

*   **High CPU Utilization:** `EC2-CPU-High-<InstanceId>` (Threshold: >=80% for 10 minutes)
*   **Instance Status Check Failed:** `EC2-StatusCheckFailed-Instance-<InstanceId>` (Threshold: >=1 for 5 minutes)
*   **System Status Check Failed:** `EC2-StatusCheckFailed-System-<InstanceId>` (Threshold: >=1 for 5 minutes)

**For Application Load Balancers (ALB):**

*   **HTTP 5xx Errors:** `ALB-HTTP-5XX-High-<ALB_Name>` (Threshold: >=1 error in 5 minutes)
*   **Low Healthy Host Count:** `ALB-HealthyHost-Low-<ALB_Name>` (Threshold: <1 healthy host in 5 minutes)

**For RDS DB Instances:**

*   **High CPU Utilization:** `RDS-CPU-High-<DBInstanceIdentifier>` (Threshold: >=70% for 10 minutes)
*   **Low Freeable Memory:** `RDS-FreeableMemory-Low-<DBInstanceIdentifier>` (Threshold: <100MB for 10 minutes)
*   **High Database Connections:** `RDS-DBConnections-High-<DBInstanceIdentifier>` (Threshold: >=80 connections for 10 minutes)

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).