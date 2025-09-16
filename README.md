# 📩 Crawl4AI Gmail POC

This project is a **proof of concept (POC)** for crawling Gmail inbox content, transforming it with an LLM, and storing structured results into MongoDB.
It combines:

* **[Crawl4AI](https://github.com/unclecode/crawl4ai)** → to automate Gmail login and scrape inbox content.
* **Groq LLM** → to parse raw HTML into structured JSON.
* **FastAPI** → to provide an API endpoint that stores parsed results.
* **MongoDB** → to persist the structured email data.

---

## ⚙️ Features

* Automates Gmail login (with username/password).
* Searches Gmail inbox for a keyword (default: `"security"`).
* Scrapes the search result rows directly from the Gmail UI.
* Uses **Groq’s LLM** to parse the raw HTML into JSON:

  ```json
  {
    "emails": [
      {
        "sender": "example@example.com",
        "subject": "Your account update",
        "snippet": "Some preview text here...",
        "time": "Sep 15, 2025"
      }
    ]
  }
  ```
* Uploads the structured JSON to a **FastAPI endpoint**.
* FastAPI saves the results into MongoDB.

---

## 📂 Project Structure

```
.
├── crawler.py   # Gmail crawler + Groq transformer + uploader
├── main.py      # FastAPI + MongoDB API server
├── .env         # Environment variables
└── requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root with:

```env
# Gmail login credentials (for POC only; see note on 2FA)
GMAIL_USER=your_email@gmail.com
GMAIL_PASSWORD=your_password

# Groq API key
GROQ_API_KEY=your_groq_api_key

# MongoDB connection
MONGO_URI=mongodb://localhost:27017
```

⚠️ **Note**: This demo assumes password login without 2FA. For accounts with 2FA, consider using OAuth2 or IMAP with app passwords.

---

## ▶️ How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

(Dependencies include: `crawl4ai`, `groq`, `fastapi`, `uvicorn`, `pymongo`, `python-dotenv`, `requests`)

---

### 2. Start FastAPI backend

```bash
uvicorn main:app --reload
```

* Runs the API server at: `http://127.0.0.1:8000`
* Endpoint available:

  * `POST /upload-emails/` → stores parsed email data into MongoDB

---

### 3. Run Gmail Crawler

In another terminal:

```bash
python crawler.py
```

* Automates Gmail login.
* Runs a keyword search (default `"security"`).
* Scrapes inbox results.
* Uses Groq LLM to parse into structured JSON.
* Sends JSON to the FastAPI endpoint → MongoDB.

---

### 4. Check MongoDB

```bash
mongo
use email_data
db.parsed_emails.find().pretty()
```

---

## 📝 Example Output in Terminal

```bash
✅ Login successful!
Step 4: Performing search for 'security'...
✅ Search complete. Email rows scraped.
Step 5: Sending 20000 characters of content to Groq...
✅ Groq Response (JSON): {'emails': [{'sender': 'alerts@google.com', 'subject': 'Security alert', 'snippet': 'New login detected...', 'time': 'Sep 16, 2025'}]}
Step 6: Uploading transformed data to FastAPI endpoint...

🎉 SUCCESS! Data uploaded to MongoDB successfully! 🎉
API Response: {'status': 'success', 'message': '1 emails stored successfully.', 'inserted_ids': ['68c9c809e672582162a5a888']}
```

---

## 🚧 Limitations

* Gmail DOM can change; selectors may break.
* Does not handle **2FA login**. Use a dummy test account without 2FA for POC.
* For production: switch to **Gmail API (OAuth2)** instead of crawling the UI.

---

## 📌 Roadmap

* [ ] Add OAuth2 Gmail API integration.
* [ ] Support attachments.
* [ ] Provide retrieval API (`GET /emails/`).
* [ ] Dockerize for easier deployment.

---

Would you like me to also include a **sample `requirements.txt`** so someone cloning this repo can `pip install -r requirements.txt` without hunting dependencies?
