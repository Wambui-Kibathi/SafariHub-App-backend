import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")  # e.g., "no-reply@safarihub.com"

def send_email(to_email, subject, html_content):
    """
    Send an email via SendGrid.
    """
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return {"status_code": response.status_code, "body": response.body}
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")