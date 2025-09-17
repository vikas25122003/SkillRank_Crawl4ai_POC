import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

# --- 1. SETUP ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
app = FastAPI()

# --- 2. DATABASE CONNECTION ---
try:
    client = MongoClient(MONGO_URI)
    client.admin.command("ping")
    db = client.email_data
    collection = db.parsed_emails
    print("✅ Successfully connected to MongoDB.")
except Exception as e:
    print(f"❌ Could not connect to MongoDB: {e}")
    exit()

# --- 3. NEW DATA MODELS ---
class EmailItem(BaseModel):
    sender: str
    subject: str
    snippet: str | None = None
    time: str | None = None

class EmailBatch(BaseModel):
    emails: list[EmailItem]

# --- 4. API ENDPOINT ---
@app.post("/upload-emails/")
async def upload_emails(batch: EmailBatch):
    try:
        docs = [email.model_dump() for email in batch.emails]
        result = collection.insert_many(docs)
        print(f"Received and stored {len(docs)} emails.")
        return {
            "status": "success",
            "message": f"{len(docs)} emails stored successfully.",
            "inserted_ids": [str(i) for i in result.inserted_ids],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
