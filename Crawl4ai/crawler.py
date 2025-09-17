import os
import asyncio
import json
import requests
from dotenv import load_dotenv
from groq import Groq
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig

# --- 1. SETUP ---
load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- 2. CONFIGURE CRAWLER & GROQ CLIENT ---
browser_config = BrowserConfig(headless=False)
crawler = AsyncWebCrawler(config=browser_config)
groq_client = Groq(api_key=GROQ_API_KEY)


# --- 3. MAIN AUTOMATION LOGIC ---
async def login_and_process_emails():
    gmail_session_id = "my-gmail-login-session"
    
    try:
        await crawler.start()

        # --- Login Flow ---
        print("Performing login...")
        await crawler.arun(
            url="https://gmail.com",
            config=CrawlerRunConfig(
                session_id=gmail_session_id,
                cache_mode=CacheMode.BYPASS
            )
        )

        js_enter_email = f"""
            document.querySelector('#identifierId').value = '{GMAIL_USER}';
            document.querySelector('#identifierNext').click();
        """
        await crawler.arun(
            url="https://gmail.com",
            config=CrawlerRunConfig(
                session_id=gmail_session_id,
                js_code=js_enter_email,
                js_only=True,
                wait_for="css:input[name='Passwd']",
                cache_mode=CacheMode.BYPASS
            )
        )
        
        js_enter_password = f"""
            document.querySelector('input[name="Passwd"]').value = '{GMAIL_PASSWORD}';
            document.querySelector('#passwordNext').click();
        """
        await crawler.arun(
            url="https://gmail.com",
            config=CrawlerRunConfig(
                session_id=gmail_session_id,
                js_code=js_enter_password,
                js_only=True,
                wait_for='css:input[aria-label="Search mail"]',
                wait_for_timeout=300000,
                cache_mode=CacheMode.BYPASS
            )
        )
        print("✅ Login successful!")

        await asyncio.sleep(10)

        # --- STEP 4: Perform Search and Scrape EMAIL ROWS ---
        print("Step 4: Performing search for 'security'...")
        search_query = "security"
        js_search_mail = f"""
            document.querySelector('input[aria-label="Search mail"]').value = '{search_query}';
            document.querySelector('button[aria-label="Search mail"]').click();
        """
        await crawler.arun(
            url="https://gmail.com",
            config=CrawlerRunConfig(
                session_id=gmail_session_id,
                js_code=js_search_mail,
                js_only=True
            )
        )

        await asyncio.sleep(5)  # let Gmail render results

        result = await crawler.arun(
            url="https://gmail.com",
            config=CrawlerRunConfig(
                session_id=gmail_session_id,
                wait_for="css:tr.zA",   # ✅ read + unread emails
                wait_for_timeout=120000,
                css_selector="tr.zA",   # ✅ only scrape email rows
                delay_before_return_html=5
            )
        )
        print("✅ Search complete. Email rows scraped.")

        # --- STEP 5: Transform with LLM ---
        raw_html_content = result.html
        if not raw_html_content:
            raise Exception("Failed to extract HTML.")
        
        truncated_html = raw_html_content[:20000]
        print(f"Step 5: Sending {len(truncated_html)} characters of content to Groq...")

        chat_messages = [
            {
                "role": "system",
                "content": (
                    "You are an intelligent Gmail email parser. "
                    "You will be given raw HTML containing multiple <tr class='zA'> rows. "
                    "Each row represents one email in Gmail search results. "
                    "Extract ALL emails as a JSON list. "
                    "For each email include: sender, subject, snippet (if visible), and time. "
                    "Format strictly as {\"emails\": [ {\"sender\":..., \"subject\":..., \"snippet\":..., \"time\":...}, ... ]}."
                )
            },
            {
                "role": "user",
                "content": f"Here is the Gmail HTML snippet:\n\n---\n{truncated_html}\n---"
            }
        ]
        
        chat_completion = groq_client.chat.completions.create(
            messages=chat_messages,
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
        )
        
        response_content = chat_completion.choices[0].message.content
        parsed_json = json.loads(response_content)
        print("✅ Groq Response (JSON):", parsed_json)

        # --- STEP 6: Upload to Database ---
        print("Step 6: Uploading transformed data to FastAPI endpoint...")
        api_url = "http://127.0.0.1:8000/upload-emails/"
        response = requests.post(api_url, json=parsed_json)
        
        if response.status_code == 200:
            print("\n🎉 SUCCESS! Data uploaded to MongoDB successfully! 🎉")
            print("API Response:", response.json())
        else:
            print(f"❌ API upload failed with status {response.status_code}: {response.text}")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        print("Closing the browser.")
        await crawler.close()


# --- EXECUTION ---
if __name__ == "__main__":
    asyncio.run(login_and_process_emails())
