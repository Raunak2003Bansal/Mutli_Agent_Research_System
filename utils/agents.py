from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
from utils.tools import web_search, scrape_url
from utils.prompts import question_variation_prompt, parser, summarizer_prompt, query_parser
from utils.pydantic_output import various_search_queries
import os
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

llm = ChatDeepSeek(
    model = "deepseek-v4-flash",
    temperature=0.2
)

question_variations_chain = question_variation_prompt | llm | query_parser

def run_scraping_pipeline(topic: str) -> list:
    result = question_variations_chain.invoke({"topic": topic})
    question_variations = [result.query1, result.query2, result.query3]
    print(f"Generated search queries: {question_variations}")
    with ThreadPoolExecutor(max_workers=3) as executor:
        # This triggers all 3 web searches at the exact same time
        search_results = executor.map(web_search, question_variations)
    
    # Flatten the list of lists into a single URLs list
    urls = []
    for url_list in search_results:
        if url_list: # Protective check in case a search returns None or empty
            urls.extend(url_list)
            
    # Deduplicate while keeping order
    unique_urls = list(dict.fromkeys(urls))
    return unique_urls



def web_scrapping_parallel(unique_urls: list, max_workers: int = 15) -> str:
    content = ""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(scrape_url, unique_urls)
    
    # Zip the URLs and their corresponding results together to build your string
    for url, scrapped in zip(unique_urls, results):
        if scrapped and not scrapped.startswith("SCRAPE_FAILED"):
            content += f"URL: {url}\nContent: {scrapped}\n\n"

    # Print first 500 chars for brevity
    print(f"Scraped content : {content[:500]}...")  
    return content
    
    

writer_chain = summarizer_prompt | llm | parser