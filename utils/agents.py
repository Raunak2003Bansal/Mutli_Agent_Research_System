from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
from utils.tools import web_search, scrape_url
from utils.prompts import question_variation_prompt, parser, summarizer_prompt, query_parser
from utils.pydantic_output import various_search_queries
import os

load_dotenv()

llm = ChatDeepSeek(
    model = "deepseek-v4-flash",
    temperature=0.2
)

question_variations_chain = question_variation_prompt | llm | query_parser

def run_scraping_pipeline(topic: str) -> str:
    result = question_variations_chain.invoke({"topic": topic})
    question_variations = [result.query1, result.query2, result.query3]
    print(f"Generated search queries: {question_variations}")

    # Search and deduplicate
    urls = []
    for query in question_variations:
        urls.extend(web_search(query))
    unique_urls = list(dict.fromkeys(urls))
    print(f"Unique URLs to scrape: {unique_urls}")
    # Scrape and filter failures
    content = ""
    for url in unique_urls:
        scrapped = scrape_url(url)
        if not scrapped.startswith("SCRAPE_FAILED"):
            content += f"URL: {url}\nContent: {scrapped}\n\n"

    # Return empty string if nothing scraped
    # Let run_research_pipeline handle the empty case
    print(f"Scraped content : {content[:500]}...")  # Print first 500 chars for brevity
    return content

writer_chain = summarizer_prompt | llm | parser