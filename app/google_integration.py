from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings

def get_google_auth_url():
    """
    Generates the Google OAuth 2.0 authorization URL for user consent.
    """
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_OAUTH["client_id"],
                "client_secret": settings.GOOGLE_OAUTH["client_secret"],
                "redirect_uris": settings.GOOGLE_OAUTH["redirect_uri"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/gmail.send"],
    )
    flow.redirect_uri = settings.GOOGLE_OAUTH["redirect_uri"]
    authorization_url, _ = flow.authorization_url(prompt="consent")
    print("Authorizatin URL generated..!", authorization_url)
    return authorization_url



##############################################
from googleapiclient.errors import HttpError


def fetch_google_emails(credentials):
    """
    Fetches email messages from the user's Gmail inbox using the provided credentials.
    Retrieves the full content of each message.
    """
    try:
        service = build("gmail", "v1", credentials=credentials)

        # Fetch the list of emails
        response = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=2).execute()
        messages = response.get("messages", [])

        if not messages:
            return []

        full_emails = []

        for message in messages:
            # Fetch the full email details
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            full_emails.append({
                "id": msg["id"],
                "snippet": msg.get("snippet", ""),
                "payload": msg.get("payload", {}),
                "threadId": msg.get("threadId"),
            })
        print("Here email fetching completed....!")

        return full_emails

    except HttpError as error:
        print(f"Error fetching emails: {error}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
from email.mime.text import MIMEText
import base64


def send_email_response(credentials, to_email, subject, body):
    """
    Sends an email response using Gmail API.
    """
    try:
        service = build("gmail", "v1", credentials=credentials)

        # Construct the email message
        message = MIMEText(body)
        message["to"] = to_email
        message["subject"] = subject

        # Encode the message in base64
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        # Send the email
        sent_message = service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        print(f"Email sent successfully to {to_email}: {sent_message['id']}")
        return True

    except HttpError as error:
        print(f"Error sending email to {to_email}: {error}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
