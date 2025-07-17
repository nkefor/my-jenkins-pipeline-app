# Automated Database Backup: AWS RDS to S3

This project provides a Python script and detailed instructions to automate the process of taking an AWS RDS snapshot and then exporting it to an S3 bucket for long-term retention, analytics, or disaster recovery.

## Table of Contents

- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
- [Detailed Workflow](#detailed-workflow)
- [Prerequisites](#prerequisites)
- [IAM Role Setup for RDS Export](#iam-role-setup-for-rds-export)
- [KMS Key Policy (if using KMS)](#kms-key-policy-if-using-kms)
- [Python Script (`rds_s3_backup.py`)](#python-script-rds_s3_backup.py)
- [How to Use](#how-to-use)
- [Diagrams](#diagrams)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Regular database backups are critical for data recovery and business continuity. AWS RDS provides automated backups and manual snapshots. For long-term archival, cross-region replication, or integration with other data lakes, exporting these snapshots to S3 is a common and highly recommended practice. This solution automates that export process.

## Architecture Overview

*(Diagram Placeholder: A high-level diagram showing the flow. Nodes: RDS DB Instance, AWS Lambda (running the Python script), S3 Bucket, KMS Key, IAM Role. Arrows: Lambda triggers RDS snapshot, RDS exports snapshot to S3 using IAM Role and KMS Key.)*

## Detailed Workflow

*(Diagram Placeholder: A more detailed sequence diagram or flowchart showing the steps.)*

**Description of Diagram:**

1.  **Trigger:** The Python script (executed by Lambda/Cron) is initiated.
2.  **Script calls RDS API:** The script sends a request to RDS to create a manual snapshot of the specified DB instance.
3.  **RDS creates Snapshot:** RDS performs the snapshot operation.
4.  **Script polls Snapshot Status:** The script continuously checks the status of the snapshot until it becomes `available`.
5.  **Script calls RDS Export API:** Once the snapshot is `available`, the script initiates an export task from RDS to S3, specifying the S3 bucket, IAM role, and KMS key.
6.  **RDS exports to S3:** RDS streams the snapshot data to the designated S3 bucket, encrypted using the KMS key.
7.  **Script monitors Export Status:** The script monitors the export task until it completes (`COMPLETED` or `FAILED`).
8.  **Completion/Failure:** The script logs the outcome.

## Prerequisites

1.  **AWS Account:** An active AWS account.
2.  **AWS CLI Configured:** Ensure your AWS CLI is configured with credentials that have permissions to create/manage RDS snapshots, S3 buckets, IAM roles, and KMS keys.
3.  **`boto3`:** The AWS SDK for Python. Install it: `pip install boto3`.
4.  **Existing RDS DB Instance:** The database you wish to back up.
5.  **Existing S3 Bucket:** The S3 bucket where snapshots will be exported.
6.  **AWS KMS Key (Optional but Recommended):** A Customer Master Key (CMK) in AWS KMS for encrypting the exported data in S3.
7.  **IAM Role for RDS Export:** A dedicated IAM role that RDS can assume to perform the export.

## IAM Role Setup for RDS Export

This is crucial. RDS needs permission to write to your S3 bucket and use your KMS key.

1.  **Create IAM Policy (`rds-s3-export-policy.json`):**
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:DeleteObject"
                ],
                "Resource": [
                    "arn:aws:s3:::your-backup-bucket-name",
                    "arn:aws:s3:::your-backup-bucket-name/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "kms:Encrypt",
                    "kms:Decrypt",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:DescribeKey"
                ],
                "Resource": "arn:aws:kms:your-region:your-account-id:key/your-kms-key-id"
            }
        ]
    }
    ```
    *   Replace `your-backup-bucket-name`, `your-region`, `your-account-id`, and `your-kms-key-id` with your actual values.
2.  **Create IAM Role:**
    *   Go to AWS IAM Console -> Roles -> Create role.
    *   **Trusted entity type:** `AWS service`.
    *   **Use case:** `RDS`.
    *   **Permissions:** Attach the policy you just created.
    *   **Role name:** `RDS-S3-Export-Role` (or a descriptive name).
    *   Note down the **Role ARN**.

## KMS Key Policy (if using KMS)

If you use a KMS key, its key policy must allow the `rds.amazonaws.com` service principal to use it for encryption.

1.  Go to AWS KMS Console -> Customer managed keys.
2.  Select your key.
3.  Go to the **Key policy** tab.
4.  Add a statement similar to this (replace `your-account-id` and `your-kms-key-id`):
    ```json
    {
        "Sid": "Allow RDS to use KMS key for S3 export",
        "Effect": "Allow",
        "Principal": {
            "Service": "rds.amazonaws.com"
        },
        "Action": [
            "kms:Encrypt",
            "kms:Decrypt",
            "kms:ReEncrypt*",
            "kms:GenerateDataKey*",
            "kms:DescribeKey"
        ],
        "Resource": "arn:aws:kms:your-region:your-account-id:key/your-kms-key-id"
    }
    ```

## Python Script (`rds_s3_backup.py`)

```python
import boto3
import datetime
import time
import argparse
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_rds_client(region):
    """Initializes and returns an RDS client."""
    try:
        return boto3.client('rds', region_name=region)
    except Exception as e:
        logging.error(f"Failed to initialize RDS client: {e}")
        sys.exit(1)

def create_rds_snapshot(rds_client, db_instance_identifier, snapshot_id_prefix):
    """ Creates a manual RDS snapshot and returns its ARN. """
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    snapshot_identifier = f"{snapshot_id_prefix}-{timestamp}"
    logging.info(f"Attempting to create snapshot '{snapshot_identifier}' for DB instance '{db_instance_identifier}'...")

    try:
        response = rds_client.create_db_snapshot(
            DBInstanceIdentifier=db_instance_identifier,
            DBSnapshotIdentifier=snapshot_identifier
        )
        snapshot_arn = response['DBSnapshot']['DBSnapshotArn']
        logging.info(f"Snapshot creation initiated. ARN: {snapshot_arn}")
        return snapshot_identifier, snapshot_arn
    except rds_client.exceptions.DBSnapshotAlreadyExistsFault:
        logging.warning(f"Snapshot '{snapshot_identifier}' already exists. Skipping creation.")
        return snapshot_identifier, None # Indicate it already exists
    except Exception as e:
        logging.error(f"Error creating snapshot for '{db_instance_identifier}': {e}")
        sys.exit(1)

def wait_for_snapshot_available(rds_client, snapshot_identifier, timeout_minutes=60, poll_interval_seconds=30):
    """ Waits for an RDS snapshot to become 'available'. """
    logging.info(f"Waiting for snapshot '{snapshot_identifier}' to become 'available'...")
    start_time = time.time()
    while True:
        if (time.time() - start_time) / 60 > timeout_minutes:
            logging.error(f"Timeout waiting for snapshot '{snapshot_identifier}' to become available.")
            sys.exit(1)
        try:
            response = rds_client.describe_db_snapshots(DBSnapshotIdentifier=snapshot_identifier)
            status = response['DBSnapshots'][0]['Status']
            logging.info(f"Snapshot '{snapshot_identifier}' status: {status}")
            if status == 'available':
                logging.info(f"Snapshot '{snapshot_identifier}' is now available.")
                return True
            elif status in ['creating', 'backing-up', 'restoring', 'modifying']:
                time.sleep(poll_interval_seconds)
            else:
                logging.error(f"Snapshot '{snapshot_identifier}' entered an unexpected state: {status}")
                sys.exit(1)
        except rds_client.exceptions.DBSnapshotNotFoundFault:
            logging.error(f"Snapshot '{snapshot_identifier}' not found while waiting for availability.")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error describing snapshot '{snapshot_identifier}': {e}")
            sys.exit(1)

def export_snapshot_to_s3(rds_client, snapshot_identifier, s3_bucket_name, iam_role_arn, kms_key_arn=None):
    """ Exports an RDS snapshot to an S3 bucket. """
    export_task_identifier = f"export-{snapshot_identifier}"
    logging.info(f"Attempting to export snapshot '{snapshot_identifier}' to S3 bucket '{s3_bucket_name}'...")

    try:
        params = {
            'ExportTaskIdentifier': export_task_identifier,
            'SourceArn': f"arn:aws:rds:{rds_client.meta.region_name}:{boto3.client('sts').get_caller_identity()['Account']}:snapshot:{snapshot_identifier}",
            'S3BucketName': s3_bucket_name,
            'IamRoleArn': iam_role_arn,
            'KmsKeyId': kms_key_arn if kms_key_arn else 'aws/rds' # Use default RDS KMS if not specified
        }
        if not kms_key_arn:
            del params['KmsKeyId'] # Remove if not provided to use default S3 encryption or bucket default

        response = rds_client.start_export_task(**params)
        logging.info(f"Export task '{export_task_identifier}' initiated. Status: {response['Status']}")
        return export_task_identifier
    except rds_client.exceptions.ExportTaskAlreadyExistsFault:
        logging.warning(f"Export task '{export_task_identifier}' already exists. Skipping initiation.")
        return export_task_identifier
    except Exception as e:
        logging.error(f"Error initiating export task for snapshot '{snapshot_identifier}': {e}")
        sys.exit(1)

def wait_for_export_completion(rds_client, export_task_identifier, timeout_minutes=180, poll_interval_seconds=60):
    """ Waits for an S3 export task to complete. """
    logging.info(f"Waiting for export task '{export_task_identifier}' to complete...")
    start_time = time.time()
    while True:
        if (time.time() - start_time) / 60 > timeout_minutes:
            logging.error(f"Timeout waiting for export task '{export_task_identifier}' to complete.")
            sys.exit(1)
        try:
            response = rds_client.describe_export_tasks(ExportTaskIdentifier=export_task_identifier)
            status = response['ExportTasks'][0]['Status']
            logging.info(f"Export task '{export_task_identifier}' status: {status}")
            if status == 'COMPLETED':
                logging.info(f"Export task '{export_task_identifier}' completed successfully.")
                return True
            elif status == 'FAILED':
                failure_cause = response['ExportTasks'][0].get('FailureCause', 'Unknown')
                logging.error(f"Export task '{export_task_identifier}' failed. Cause: {failure_cause}")
                sys.exit(1)
            elif status in ['CREATING', 'STARTING', 'IN_PROGRESS', 'CANCELLING']:
                time.sleep(poll_interval_seconds)
            else:
                logging.error(f"Export task '{export_task_identifier}' entered an unexpected state: {status}")
                sys.exit(1)
        except rds_client.exceptions.ExportTaskNotFoundFault:
            logging.error(f"Export task '{export_task_identifier}' not found while waiting for completion.")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error describing export task '{export_task_identifier}': {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Automate AWS RDS snapshot creation and export to S3."
    )
    parser.add_argument("--region", required=True, help="AWS region (e.g., us-east-1)")
    parser.add_argument("--db-instance-identifier", required=True,
                        help="The DB instance identifier of the RDS database to backup.")
    parser.add_argument("--snapshot-id-prefix", default="manual-backup",
                        help="Prefix for the generated snapshot identifier (e.g., 'my-app-daily-backup').")
    parser.add_argument("--s3-bucket-name", required=True,
                        help="The S3 bucket name where the snapshot will be exported.")
    parser.add_argument("--iam-role-arn", required=True,
                        help="The ARN of the IAM role that grants RDS permission to export to S3 and use KMS.")
    parser.add_argument("--kms-key-arn",
                        help="The ARN of the KMS key to use for encrypting the exported data in S3 (optional).")

    args = parser.parse_args()

    rds_client = get_rds_client(args.region)

    # 1. Create RDS Snapshot
    snapshot_identifier, _ = create_rds_snapshot(rds_client, args.db_instance_identifier, args.snapshot_id_prefix)
    if not snapshot_identifier: # If snapshot already existed and was skipped
        logging.info("Using existing snapshot for export.")
    else:
        wait_for_snapshot_available(rds_client, snapshot_identifier)

    # 2. Export Snapshot to S3
    export_task_identifier = export_snapshot_to_s3(
        rds_client,
        snapshot_identifier,
        args.s3_bucket_name,
        args.iam_role_arn,
        args.kms_key_arn
    )

    # 3. Wait for Export Completion
    if export_task_identifier:
        wait_for_export_completion(rds_client, export_task_identifier)
    else:
        logging.info("No new export task initiated (possibly already running or completed).")

    logging.info("RDS to S3 backup process completed.")

if __name__ == "__main__":
    main()