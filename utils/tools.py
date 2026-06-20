from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()


#create a tavily client
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
def web_search(query: str) -> str:
    try:
        results = tavily.search(query = query, max_results = 5, days=30)
        out = []
        for r in results["results"]:
            out.append(f"{r['url']}")
    
        return out
    
    except Exception as e:
        return []



def scrape_url(url: str) -> str:
    try:
        resp = requests.get(url, timeout=5, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xhtml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "identity",  # ← prevents compressed responses
            "Accept-Language": "en-US,en;q=0.5",
        })

        if resp.status_code in (403, 401, 429):
            return f"SCRAPE_FAILED: HTTP {resp.status_code} for {url}"

        # Detect binary/garbled content before parsing
        try:
            resp.text.encode("utf-8")
        except Exception:
            return f"SCRAPE_FAILED: Binary or undecodable content at {url}"

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        text = text.encode("utf-8", errors="ignore").decode("utf-8")

        # Detect garbled output — valid pages have real words
        if len(text.strip()) < 200:
            return f"SCRAPE_FAILED: Page too short or empty at {url}"

        # Detect non-text content (high ratio of non-ASCII characters)
        non_ascii = sum(1 for c in text if ord(c) > 127)
        if non_ascii / max(len(text), 1) > 0.3:  # >30% non-ASCII = garbled
            return f"SCRAPE_FAILED: Garbled or encoded content at {url}"

        FAILURE_SIGNALS = [
            "enable javascript", "enable js", "please enable",
            "ad blocker", "captcha", "access denied",
            "subscribe to read", "sign in to",
        ]
        if any(signal in text.lower() for signal in FAILURE_SIGNALS):
            return f"SCRAPE_FAILED: Page blocked or requires login at {url}"

        return text[:3000]

    except requests.exceptions.Timeout:
        return f"SCRAPE_FAILED: Timeout for {url}"
    except Exception as e:
        return f"SCRAPE_FAILED: {str(e)} for {url}"


if __name__ == "__main__":
    # Example usage of the web_search tool
    query = "What is the latest news on War between Iran and America?"
    search_results = web_search.invoke(query)
    print(search_results)
    # Example usage of the scrape_url tool
    # url = "https://americaweekly.com/iran-america-war-live-updates-2026/"
    # scraped_content = scrape_url.invoke(url)
    # print(scraped_content)