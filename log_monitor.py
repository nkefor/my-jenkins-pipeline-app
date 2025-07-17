import time
import re
import argparse
import os

def monitor_log(log_file_path):
    """Monitors a log file for security-related patterns in real-time."""
    # Define security patterns (regex) and their corresponding alert messages
    security_patterns = [
        {
            "pattern": r"authentication failure|failed password",
            "message": "[SECURITY ALERT] Failed login attempt detected!",
            "level": "CRITICAL"
        },
        {
            "pattern": r"sudo: .*COMMAND=\/bin\/(bash|sh)",
            "message": "[SECURITY ALERT] Suspicious sudo to shell command!",
            "level": "HIGH"
        },
        {
            "pattern": r"useradd|usermod|groupadd|groupmod",
            "message": "[SECURITY ALERT] User/Group modification detected!",
            "level": "MEDIUM"
        },
        {
            "pattern": r"sshd: session opened for user root",
            "message": "[SECURITY ALERT] Root SSH session opened!",
            "level": "HIGH"
        },
        {
            "pattern": r"rm -rf|chmod 777|chown root",
            "message": "[SECURITY ALERT] Potentially destructive or privilege-changing command!",
            "level": "HIGH"
        },
        {
            "pattern": r"CRON \(root\) CMD",
            "message": "[INFO] Root CRON job executed.",
            "level": "LOW"
        }
    ]

    print(f"Monitoring log file: {log_file_path} for security events...")
    print("Press Ctrl+C to stop.")

    try:
        # Open the file and seek to the end to only read new lines
        with open(log_file_path, 'r') as f:
            f.seek(0, os.SEEK_END)

            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)  # Sleep briefly if no new lines
                    continue

                # Process the new line
                for pattern_info in security_patterns:
                    if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                        color_code = "\033[0m" # Reset
                        if pattern_info["level"] == "CRITICAL":
                            color_code = "\033[91m" # Red
                        elif pattern_info["level"] == "HIGH":
                            color_code = "\033[93m" # Yellow
                        elif pattern_info["level"] == "MEDIUM":
                            color_code = "\033[94m" # Blue

                        print(f"{color_code}{pattern_info["message"]} (Level: {pattern_info["level"]})\033[0m")
                        print(f"    Log Entry: {line.strip()}")
                        print("-" * 60)

    except FileNotFoundError:
        print(f"Error: Log file not found at '{log_file_path}'. Please check the path.")
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Real-time log monitor for security events."
    )
    parser.add_argument(
        "log_file",
        help="The path to the log file to monitor (e.g., /var/log/auth.log, /var/log/syslog)."
    )
    args = parser.parse_args()

    monitor_log(args.log_file)

if __name__ == "__main__":
    main()
