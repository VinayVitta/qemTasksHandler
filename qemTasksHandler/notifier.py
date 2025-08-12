# Title: Email
# Author: Vinay Vitta | Qlik - QDI PS
# Date: August 2025

# Description: Email aLerts
# Example to send an email
# Update with the right SMTP server and port numbers
#   SMTP_SERVER = "mailhub.carcgl.com"
#   SMTP_PORT =  25
#   SENDER_EMAIL = "noreply@dev-qem-script"
#   SENDER_PASSWORD = ""


import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(sender_email, receiver_email, subject, body, attachment_path):
    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = ", ".join(receiver_email)
    message['Subject'] = subject

    # Attach body
    message.attach(MIMEText(body, 'plain'))

    # Attach file
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {attachment_path}",
    )

    message.attach(part)

    # Connect to SMTP server
    server = smtplib.SMTP('mailhub.carcgl.com', 25)
    server.starttls()

    # Login
    # server.login(sender_email, sender_password)

    # Send email
    server.sendmail(sender_email, receiver_email, message.as_string())

    # Quit SMTP server
    server.quit()


if __name__ == "__main__":
    # Example usage
    sender_email = "noreply@dev-qem-script"
    # sender_password = 'your_password'
    receiver_email = 'test@emailServer.com'
    subject = 'Test Email with Attachment'
    body = 'This is a test email sent from Python.'
    attachment_path = r'D:\Attunity\RowCountValidation-master-3.1.0\RowCountValidation-master\data\output\RowCount_output_2024_04_26_14_16_54.xlsx'
    send_email(sender_email, receiver_email, subject, body, attachment_path)
    print("test is good")
