import os
import base64
from dotenv import load_dotenv
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- 1. SETUP ---
load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            print("✅ Authentication successful. Token saved to token.json")
    return build("gmail", "v1", credentials=creds)

def get_email_body(payload):
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain" and "data" in part["body"]:
                data = part["body"]["data"]
                body = base64.urlsafe_b64decode(data.encode("UTF-8")).decode("UTF-8")
                break
    elif "body" in payload and "data" in payload["body"]:
        data = payload["body"]["data"]
        body = base64.urlsafe_b64decode(data.encode("UTF-8")).decode("UTF-8")
    return body

def process_emails():
    try:
        print("Authenticating with Gmail API...")
        service = authenticate_gmail()
        print("✅ Successfully connected to Gmail API.")

        search_query = "security"
        print(f"Step 3: Searching for emails with query: '{search_query}'...")
        results = service.users().messages().list(userId="me", q=search_query).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No emails found for the given query.")
            return

        print(f"✅ Found {len(messages)} emails. Extracting details...")
        email_batch = {"emails": []}

        for message in messages[:20]:
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            headers = msg["payload"]["headers"]
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "No Sender")
            time = next((h["value"] for h in headers if h["name"] == "Date"), None)
            snippet = msg.get("snippet", "")
            body = get_email_body(msg["payload"])
            email_item = {"sender": sender, "subject": subject, "snippet": snippet, "time": time, "body": body}
            email_batch["emails"].append(email_item)

        print(f"✅ Extracted data for {len(email_batch['emails'])} emails.")

        if not email_batch["emails"]:
            print("No data extracted to upload.")
            return
            
        print("Step 5: Uploading extracted data to FastAPI endpoint...")
        api_url = "http://127.0.0.1:8000/upload-emails/"
        response = requests.post(api_url, json=email_batch)
        
        if response.status_code == 200:
            print("\n🎉 SUCCESS! Data uploaded to MongoDB successfully! 🎉")
            print("API Response:", response.json())
        else:
            print(f"❌ API upload failed with status {response.status_code}: {response.text}")

    except HttpError as error:
        print(f"An API error occurred: {error}")
    except FileNotFoundError:
        print("❌ Error: credentials.json not found. Please follow the setup steps to download it.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    process_emails()