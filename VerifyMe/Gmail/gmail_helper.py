import copy
import os
import sys
import yaml
import base64
import mimetypes

from typing import List

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication

from googleapiclient import errors

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


def create_message_without_attachment(to,
                                      subject,
                                      message_text_html,
                                      message_text_plain,
                                      bcc=[],
                                      sender=config['support_email']):
    """Create a message for an email, without an attachment.

    message_text_plain: The plain text of the email message.
    message_html_plain: The html text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = to
    message['Bcc'] = ",".join(bcc)

    message.attach(MIMEText(message_text_plain, 'plain'))
    message.attach(MIMEText(message_text_html, 'html'))

    raw_message_no_attachment = base64.urlsafe_b64encode(
        message.as_bytes()).decode()
    body = {'raw': raw_message_no_attachment}

    return body
