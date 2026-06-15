from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()


#create a tavily client
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
# creating the first tool
@tool
def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information on a given topic. 
    Returns titles, urls and snippets.

    args:
        query: The search query string.
    returns:
        A string containing the search results, including titles, urls and snippets.
    """
    try:
        results = tavily.search(query = query, max_results = 5)
        out = []
        for r in results["results"]:
            out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content']}\n")

        return "\n----\n".join(out)
    
    except Exception as e:
        return f"An error occurred during web search: {str(e)}"


# create a tool for web scraping
@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)[:2500]
        text = text.encode("utf-8", errors="ignore").decode("utf-8")
        return text
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"


from pydantic import BaseModel, Field
from typing import List

# Define a schema for an individual key finding
class KeyFinding(BaseModel):
    subheading: str = Field(
        description="A clear, actionable subheading for this finding."
    )
    explanation: str = Field(
        description="Detailed analysis, specific facts, statistics, or direct quotes, along with its implication."
    )

# Define the overall report structure
class ResearchReport(BaseModel):
    introduction: str = Field(
        description="Compelling overview establishing context and topic relevance."
    )
    key_findings: List[KeyFinding] = Field(
        description="A list containing a minimum of three (3) distinct, well-explained findings."
    )
    conclusion: str = Field(
        description="Cohesive summary synthesizing the findings into a definitive closing statement."
    )
    sources: List[str] = Field(
        description="Clean list of all source URLs successfully utilized or scraped during research."
    )

if __name__ == "__main__":
    # Example usage of the web_search tool
    query = "What is the latest news on War between Iran and America?"
    search_results = web_search.invoke(query)
    print(search_results)
    # Example usage of the scrape_url tool
    # url = "https://americaweekly.com/iran-america-war-live-updates-2026/"
    # scraped_content = scrape_url.invoke(url)
    # print(scraped_content)