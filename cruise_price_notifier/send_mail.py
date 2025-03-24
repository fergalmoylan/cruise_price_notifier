import smtplib
import ssl
from dotenv import load_dotenv
import os
from email.message import EmailMessage
import logging

log = logging.getLogger(__name__)

load_dotenv()
sender_address = os.environ.get("SENDER_ADDRESS")
sender_password = os.environ.get("SENDER_PASSWORD")


def send_mail_html(html, date, recipients):
    em = EmailMessage()
    em['From'] = sender_address
    em['To'] = recipients
    em['Subject'] = f"Cruise Prices {date}"
    em.set_content("This is an HTML email. Please view it in an HTML-compatible email client.")
    em.add_alternative(html, subtype='html')

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(sender_address, sender_password)
        smtp.sendmail(sender_address, recipients, em.as_string())
        log.info("mail sent successfully")

