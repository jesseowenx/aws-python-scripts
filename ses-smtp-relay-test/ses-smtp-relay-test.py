import smtplib
from email.mime.text import MIMEText
import credentials

smtp_server = 'email-smtp.ap-southeast-2.amazonaws.com'
smtp_port = 587
smtp_username = credentials.smtp_username
smtp_password = credentials.smtp_password
sender_email = ''
recipient_email = ''
subject = 'Test Email from AWS SES'
body = 'This is a test email sent via SES SMTP relay.'

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = sender_email
msg['To'] = recipient_email

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.set_debuglevel(1)
    server.starttls()
    server.login(smtp_username, smtp_password)
    print(f"Successfully logged in to SMTP server {smtp_server}.")

    server.sendmail(sender_email, recipient_email, msg.as_string())
    print("Test email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    server.quit()
    print("Connection to SMTP server closed")
