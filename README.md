# Gmail Processing: Web Crawler vs. API

This repository contains two different implementations for fetching and processing emails from a Gmail account, demonstrating the evolution from a fragile web-crawling Proof of Concept (PoC) to a robust, production-ready API-based solution.

1.  **Web Crawler PoC (`web_crawler_poc/`)**: A simple script using `Crawl4AI` to automate a browser, log in with a username/password, and scrape email content directly from the Gmail UI.
2.  **Gmail API (`gmail_api_production/`)**: A secure and reliable script using the official **Google Gmail API** with OAuth 2.0 to fetch emails, ensuring it's not affected by UI changes and is compatible with 2-Step Verification.

## ⭐ Comparison of Methods

| Feature              | Web Crawler (PoC)                               | Gmail API (Recommended)                                   |
| -------------------- | ----------------------------------------------- | --------------------------------------------------------- |
| **Method** | Simulates a user in a browser (Playwright)      | Direct communication with Google's servers (OAuth 2.0)    |
| **Security** | 🔴 **Low**: Requires storing password in `.env` | ✅ **High**: Uses secure, short-lived tokens. No password needed. |
| **Reliability** | 🔴 **Low**: Breaks if Gmail changes its HTML/CSS. | ✅ **High**: Based on a stable, versioned API.            |
| **2-Step Verification**| Not supported.                                  | Fully supported.                                          |
| **Setup** | Simple (install libraries, set `.env`)          | More involved (one-time Google Cloud project setup).      |
| **Use Case** | Quick, temporary prototypes.                    | Production applications, long-term and reliable tasks.    |

## 📂 Project Structure

```
.
├── .gitignore
├── README.md
├── .env
│
├── web_crawler_poc/
│   ├── crawler.py         # The crawler script
│   ├── main.py            # Its FastAPI server
│   └── requirements.txt
│
└── gmail_api_production/
    ├── gmail_api_processor.py # The API client script
    ├── main_gmail_api.py      # Its FastAPI server
    ├── requirements.txt
    └── credentials.json       # (Secret - Not in Git)
```

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-repository-name>
```

### 2. Configure Environment Variables

Create a `.env` file in the root of the project. You only need to fill in the variables for the method you intend to run.

```env
# --- For Web Crawler PoC ---
# (Use a dummy account without 2-Step Verification)
GMAIL_USER=your_dummy_email@gmail.com
GMAIL_PASSWORD=your_dummy_password
GROQ_API_KEY=your_groq_api_key

# --- For Both Implementations ---
MONGO_URI="your_mongodb_connection_string"
```

## ▶️ How to Run

You can run either implementation independently.

### Method 1: Web Crawler PoC

This method is quick to run but is not recommended for anything beyond a simple test.

1.  **Navigate to the folder:**
    ```bash
    cd web_crawler_poc
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install # Installs necessary browser binaries
    ```
3.  **Start the FastAPI server** (in one terminal):
    ```bash
    uvicorn main:app --reload
    ```
4.  **Run the crawler script** (in a second terminal):
    ```bash
    python crawler.py
    ```

### Method 2: Gmail API (Recommended)

This method is secure, reliable, and the industry-standard approach.

1.  **One-Time Setup: Google Cloud**
    * Enable the **Gmail API** in your Google Cloud project.
    * Configure the **OAuth Consent Screen** (as an External app) and add your email as a Test User.
    * Create **OAuth 2.0 Client ID** credentials for a **Desktop app**.
    * Download the JSON file, rename it to `credentials.json`, and place it inside the `gmail_api_production/` folder.

2.  **Navigate to the folder:**
    ```bash
    cd gmail_api_production
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Start the FastAPI server** (in one terminal):
    ```bash
    uvicorn main_gmail_api:app --reload
    ```
5.  **Run the API processor script** (in a second terminal):
    ```bash
    python gmail_api_processor.py
    ```
    * On the first run, a browser window will open, asking you to log in and grant permission. After approval, a `token.json` file will be created, and you won't need to log in again.
