import boto3
import argparse
import json
import sys

def create_sns_topic(sns_client, topic_name, email_address):
    """
    Creates an SNS topic and subscribes an email address to it.
    Returns the Topic ARN.
    """
    try:
        print(f"Creating SNS topic: {topic_name}...")
        response = sns_client.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        print(f"SNS Topic '{topic_name}' created with ARN: {topic_arn}")

        print(f"Subscribing {email_address} to topic {topic_name}...")
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email_address
        )
        print(f"Subscription request sent to {email_address}. Please confirm it in your email inbox.")
        return topic_arn
    except Exception as e:
        print(f"Error creating SNS topic or subscription: {e}")
        sys.exit(1)

def create_cloudwatch_alarm(cloudwatch_client, alarm_name, metric_name, namespace, statistic,
                            period, evaluation_periods, threshold, comparison_operator,
                            alarm_description, dimensions, topic_arn):
    """
    Creates or updates a CloudWatch alarm.
    """
    try:
        print(f"Creating/Updating CloudWatch Alarm: {alarm_name}...")
        cloudwatch_client.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=alarm_description,
            ActionsEnabled=True,
            MetricName=metric_name,
            Namespace=namespace,
            Statistic=statistic,
            Period=period,
            EvaluationPeriods=evaluation_periods,
            Threshold=threshold,
            ComparisonOperator=comparison_operator,
            Dimensions=dimensions,
            AlarmActions=[topic_arn],
            OKActions=[topic_arn] # Optional: Send notification when alarm returns to OK state
        )
        print(f"CloudWatch Alarm '{alarm_name}' created/updated successfully.")
    except Exception as e:
        print(f"Error creating CloudWatch Alarm '{alarm_name}': {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Set up CloudWatch Alarms for AWS application monitoring."
    )
    parser.add_argument("--region", required=True, help="AWS region (e.g., us-east-1)")
    parser.add_argument("--email", required=True, help="Email address for SNS notifications")
    parser.add_argument("--sns-topic-name", default="ApplicationHealthAlerts",
                        help="Name for the SNS topic (default: ApplicationHealthAlerts)")
    parser.add_argument("--ec2-instance-ids", nargs='*', help="Space-separated list of EC2 Instance IDs to monitor (e.g., i-xxxxxxxxxxxxxxxxx)")
    parser.add_argument("--alb-arns", nargs='*', help="Space-separated list of Application Load Balancer ARNs to monitor (e.g., arn:aws:elasticloadbalancing:REGION:ACCOUNT:loadbalancer/app/NAME/ID)")
    parser.add_argument("--rds-instance-ids", nargs='*', help="Space-separated list of RDS DB Instance Identifiers to monitor (e.g., my-database-instance)")

    args = parser.parse_args()

    # Initialize AWS clients
    try:
        sns_client = boto3.client('sns', region_name=args.region)
        cloudwatch_client = boto3.client('cloudwatch', region_name=args.region)
    except Exception as e:
        print(f"Error initializing AWS clients: {e}. Ensure your AWS credentials are configured.")
        sys.exit(1)

    # 1. Create SNS Topic
    topic_arn = create_sns_topic(sns_client, args.sns_topic_name, args.email)

    # 2. Create EC2 Alarms
    if args.ec2_instance_ids:
        print("\n--- Setting up EC2 Alarms ---")
        for instance_id in args.ec2_instance_ids:
            # EC2 CPU Utilization Alarm
            create_cloudwatch_alarm(
                cloudwatch_client,
                alarm_name=f"EC2-CPU-High-{instance_id}",
                metric_name="CPUUtilization",
                namespace="AWS/EC2",
                statistic="Average",
                period=300, # 5 minutes
                evaluation_periods=2,
                threshold=80.0,
                comparison_operator="GreaterThanOrEqualToThreshold",
                alarm_description=f"EC2 instance {instance_id} CPU utilization is consistently high (>=80% for 10 minutes).",
                dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                topic_arn=topic_arn
            )
            # EC2 Status Check Failed (Instance) Alarm
            create_cloudwatch_alarm(
                cloudwatch_client,
                alarm_name=f"EC2-StatusCheckFailed-Instance-{instance_id}",
                metric_name="StatusCheckFailed_Instance",
                namespace="AWS/EC2",
                statistic="Maximum",
                period=60, # 1 minute
                evaluation_periods=5,
                threshold=1.0,
                comparison_operator="GreaterThanOrEqualToThreshold",
                alarm_description=f"EC2 instance {instance_id} failed instance status checks (e.g., OS issues, exhausted resources).",
                dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                topic_arn=topic_arn
            )
            # EC2 Status Check Failed (System) Alarm
            create_cloudwatch_alarm(
                cloudwatch_client,
                alarm_name=f"EC2-StatusCheckFailed-System-{instance_id}",
                metric_name="StatusCheckFailed_System",
                namespace="AWS/EC2",
                statistic="Maximum",
                period=60, # 1 minute
                evaluation_periods=5,
                threshold=1.0,
                comparison_operator="GreaterThanOrEqualToThreshold",
                alarm_description=f"EC2 instance {instance_id} failed system status checks (e.g., underlying hardware issues).",
                dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                topic_arn=topic_arn
            )

    # 3. Create ALB Alarms
    if args.alb_arns:
        print("\n--- Setting up ALB Alarms ---")
        for alb_arn in args.alb_arns:
            # ALB HTTP 5xx Errors Alarm
            # Note: For more granular monitoring, you might need TargetGroup dimensions.
            # This example monitors 5xx from the LoadBalancer level.
            create_cloudwatch_alarm(
                cloudwatch_client,
                alarm_name=f"ALB-HTTP-5XX-High-{alb_arn.split('/')[-1]}", # Use part of ARN for name
                metric_name="HTTPCode_Target_5XX_Count",
                namespace="AWS/ApplicationELB",
                statistic="Sum",
                period=300, # 5 minutes
                evaluation_periods=1,
                threshold=1.0, # At least one 5xx error in 5 minutes
                comparison_operator="GreaterThanOrEqualToThreshold",
                alarm_description=f"ALB {alb_arn} is reporting HTTP 5xx errors from targets.",
                dimensions=[{'Name': 'LoadBalancer', 'Value': alb_arn.split(':loadbalancer/')[-1]}], # Extract LB part of ARN
                topic_arn=topic_arn
            )
            # ALB Healthy Host Count Low
            create_cloudwatch_alarm(
                cloudwatch_client,
                alarm_name=f"ALB-HealthyHost-Low-{alb_arn.split('/')[-1]}",
                metric_name="HealthyHostCount",
                namespace="AWS/ApplicationELB",
                statistic="Minimum",
                period=300,
                evaluation_periods=1,
                threshold=1.0, # If healthy hosts drop to 0
                comparison_operator="LessThanThreshold",
                alarm_description=f"ALB {alb_arn} has a low number of healthy hosts.",
                dimensions=[{'Name': 'LoadBalancer', 'Value': alb_arn.split(':loadbalancer/')[-1]}],
                topic_arn=topic_arn
            )

    # 4. Create RDS Alarms
    if args.rds_instance_ids:
        print("\n--- Setting up RDS Alarms ---")
        for db_instance_id in args.rds_instance_ids:
            # RDS CPU Utilization Alarm
            create_cloudwatch_alarm(
                cloudwatch_client,
                alarm_name=f"RDS-CPU-High-{db_instance_id}",
                metric_name="CPUUtilization",
                namespace="AWS/RDS",
                statistic="Average",
                period=300,
                evaluation_periods=2,
                threshold=70.0,
                comparison_operator="GreaterThanOrEqualToThreshold",
                alarm_description=f"RDS instance {db_instance_id} CPU utilization is consistently high (>=70% for 10 minutes).",
                dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
                topic_arn=topic_arn
            )
            # RDS Freeable Memory Low Alarm
            create_cloudwatch_alarm(
                cloudwatch_client,
                alarm_name=f"RDS-FreeableMemory-Low-{db_instance_id}",
                metric_name="FreeableMemory",
                namespace="AWS/RDS",
                statistic="Average",
                period=300,
                evaluation_periods=2,
                threshold=100000000.0, # e.g., 100 MB (in bytes)
                comparison_operator="LessThanThreshold",
                alarm_description=f"RDS instance {db_instance_id} has low freeable memory (<100MB for 10 minutes).",
                dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
                topic_arn=topic_arn
            )
            # RDS Database Connections High Alarm
            create_cloudwatch_alarm(
                cloudwatch_client,
                alarm_name=f"RDS-DBConnections-High-{db_instance_id}",
                metric_name="DatabaseConnections",
                namespace="AWS/RDS",
                statistic="Average",
                period=300,
                evaluation_periods=2,
                threshold=80.0, # e.g., 80 connections
                comparison_operator="GreaterThanOrEqualToThreshold",
                alarm_description=f"RDS instance {db_instance_id} has a high number of database connections (>=80 for 10 minutes).",
                dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
                topic_arn=topic_arn
            )

    print("\nMonitoring setup complete. Check your email for SNS subscription confirmation.")

if __name__ == "__main__":
    main()
