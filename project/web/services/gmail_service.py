import os
import base64
import mimetypes
import json

from email.message import EmailMessage

from django.conf import settings

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from google_auth_oauthlib.flow import Flow

from ..models import GmailConnection

#-----
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
#-----

def get_google_config():

    with open(settings.GOOGLE_CLIENT_SECRETS_FILE, "r") as f:

        config = json.load(f)

    return config["web"]

def get_google_flow(state=None):

    flow = Flow.from_client_secrets_file(

        settings.GOOGLE_CLIENT_SECRETS_FILE,

        scopes=[
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/gmail.send"
        ],

        state=state,

        redirect_uri=settings.GOOGLE_REDIRECT_URI,

        autogenerate_code_verifier=False

    )

    return flow

def exchange_code(flow, authorization_response):

    flow.fetch_token(
        authorization_response=authorization_response
    )

    credentials = flow.credentials

    return credentials

def build_gmail_service(user):

    gmail = GmailConnection.objects.get(

        user=user,

        connected=True

    )

    config = get_google_config()

    credentials = Credentials(

        token=gmail.access_token,

        refresh_token=gmail.refresh_token,

        token_uri="https://oauth2.googleapis.com/token",

        client_id=config["client_id"],

        client_secret=config["client_secret"],

        scopes=[
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/gmail.send"
        ]

    )

    # Refresh expired access token
    if credentials.expired:

        if credentials.refresh_token:

            credentials.refresh(Request())

            gmail.access_token = credentials.token

            gmail.refresh_token = credentials.refresh_token

            gmail.token_expiry = credentials.expiry

            gmail.save()

        else:

            raise Exception(
                "Google account needs to be connected again."
            )

    service = build(

        "gmail",

        "v1",

        credentials=credentials

    )

    return service

def send_gmail(
    user,
    to_email,
    subject,
    body,
    attachments=None
):

    service = build_gmail_service(user)

    message = EmailMessage()

    message["To"] = to_email

    message["Subject"] = subject

    message.set_content(body)

    if attachments:

        for file_path in attachments:

            if not os.path.exists(file_path):
                continue

            mime_type, _ = mimetypes.guess_type(file_path)

            if mime_type:
                maintype, subtype = mime_type.split("/", 1)
            else:
                maintype, subtype = "application", "octet-stream"

            with open(file_path, "rb") as f:

                message.add_attachment(

                    f.read(),

                    maintype=maintype,

                    subtype=subtype,

                    filename=os.path.basename(file_path)

                )

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    result = service.users().messages().send(

        userId="me",

        body={
            "raw": raw
        }

    ).execute()

    print(result)

    return result