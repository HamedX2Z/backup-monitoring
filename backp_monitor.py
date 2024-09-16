import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

# Configuration
BACKUP_DIR = "/var/backups"  # Directory where backups are stored
LOG_FILE = "/path/to/logfile.txt"  # Log file to record backup statuses
EXPECTED_BACKUP_FILE = "backup_{}.tar.gz".format(datetime.now().strftime("%Y-%m-%d"))
EMAIL_SENDER = "your_email@example.com"
EMAIL_RECEIVER = "your_email@example.com"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
EMAIL_USER = "your_email@example.com"
EMAIL_PASS = "your_password"

# Check backup details
def check_backup():
    report_lines = []
    report_lines.append(f"Checking backup for {datetime.now().strftime('%Y-%m-%d')}")

    # Expected backup file
    backup_file = os.path.join(BACKUP_DIR, EXPECTED_BACKUP_FILE)
    
    if os.path.exists(backup_file):
        file_size = os.path.getsize(backup_file) / (1024 * 1024)  # File size in MB
        mod_time = datetime.fromtimestamp(os.path.getmtime(backup_file)).strftime("%Y-%m-%d %H:%M:%S")
        report_lines.append(f"Backup found: {backup_file}")
        report_lines.append(f"Size: {file_size:.2f} MB")
        report_lines.append(f"Last modified: {mod_time}")
    else:
        report_lines.append(f"Backup missing: {EXPECTED_BACKUP_FILE}")
    
    report = "\n".join(report_lines)
    
    # Log the result
    log_backup_status(report)
    
    return report

# Log backup status to a file
def log_backup_status(report):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {report}\n")

# Send email report with optional attachment
def send_email(report, attach_log=False):
    msg = MIMEMultipart()
    msg["Subject"] = "Daily Backup Report"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    # Add report text
    msg.attach(MIMEText(report, "plain"))

    # Attach log file if required
    if attach_log:
        with open(LOG_FILE, "rb") as log_file:
            log_attachment = MIMEApplication(log_file.read())
            log_attachment.add_header("Content-Disposition", f"attachment; filename={os.path.basename(LOG_FILE)}")
            msg.attach(log_attachment)

    # Send the email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

# Main function
if __name__ == "__main__":
    report = check_backup()
    
    # Send email with attachment if backup is missing
    if "Backup missing" in report:
        send_email(report, attach_log=True)
    else:
        send_email(report)