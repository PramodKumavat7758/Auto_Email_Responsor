import base64
from email.mime.text import MIMEText

from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from google_auth_oauthlib.flow import Flow
from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.openai_service import analyze_email, generate_reply
from app.google_integration import fetch_google_emails

CLIENT_CONFIG = {
    "installed": {
        "client_id": "555622104966-qd1kgvnfjb914nrchjv858k6qo8a5tlc.apps.googleusercontent.com",
        "project_id": "48129",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://127.0.0.1:8000/email-handler/google-auth/callback/"],
    }
}


def google_auth(request):
    try:
        # Create a flow instance with your client configuration
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/gmail.send"],
        )
        flow.redirect_uri = CLIENT_CONFIG["installed"]["redirect_uris"][0]

        # Generate the authorization URL
        auth_url, _ = flow.authorization_url(prompt="consent")

        # Redirect the user to the Google authorization URL
        return redirect(auth_url)

    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)


def google_auth_callback(request):
    try:
        # Retrieve the state and authorization code from the request
        state = request.GET.get("state")
        code = request.GET.get("code")

        if not code:
            return HttpResponse("Error: Authorization code is missing.", status=400)

        print(f"Redirect URI in settings: {settings.GOOGLE_OAUTH['redirect_uri']}")

        # Create a Flow instance using the client configuration
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH["client_id"],
                    "client_secret": settings.GOOGLE_OAUTH["client_secret"],
                    "redirect_uris": settings.GOOGLE_OAUTH["redirect_uris"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/gmail.send"],
            state=state,  # Ensure state is properly set
        )

        flow.redirect_uri = settings.GOOGLE_OAUTH["redirect_uri"]

        # Exchange the authorization code for an access token
        flow.fetch_token(code=code)

        # Save the credentials (for simplicity, printing here)
        credentials = flow.credentials

        request.session["credentials"] ={
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret":credentials.client_secret,
            "scopes":credentials.scopes,
        }

        print(f"Access Token: {credentials.token}")
        print(f"Refresh Token: {credentials.refresh_token}")

        return render(request, "success.html", {
            "message": "Authentication successful! You can now use the application.",
        })




        #return HttpResponse("Authentication successful! Tokens fetched.")

    except Exception as e:
        # Log the error and return an appropriate response
        print(f"Error during callback: {e}")
        return HttpResponse(f"Error during callback: {e}", status=500)


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



def read_emails(request):
    # Get the stored credentials from session
    credentials_dict = request.session.get('credentials')
    if not credentials_dict:
        return HttpResponse("No credentials found. Please authenticate first.", status=401)

    credentials = Credentials.from_authorized_user_info(credentials_dict)
    emails = fetch_google_emails(credentials)

    if not emails:
        return JsonResponse({"message":"No mails found..!"})
    results =[]
    for email in emails:

        email_content= email.get("snippet","")
        headers = {header["name"]:header["value"] for header in email["payload"].get("headers",[])}
        sender_email = headers.get("From")

        if not sender_email:
            results.append({"email_id":email["id"],"status":"Failed - Sender email not found"})
            continue
        category = analyze_email(email_content)
        reply = generate_reply(email_content)

        success = send_email_response(
            credentials=credentials,
            to_email=sender_email,
            subject="Re: Your Enquery",
            body=reply
        )
        results.append({
            "email_id":email["id"],
            "sender":sender_email,
            "category":category,
            "reply_sent":success
        })

        """""
        content = email.get("snippet","No Content available")

        process_email(content)
        processed_emails.append(email["id"])

    return JsonResponse({"message": f"{len(processed_emails)}Emails processed successfully!","processed_emails":processed_emails,})
"""
    return JsonResponse({"results":results})