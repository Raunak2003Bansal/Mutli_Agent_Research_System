from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import scrape_url
from dotenv import load_dotenv
import os
load_dotenv()

# model = "llama-3.3-70b-versatile"
llm = ChatGroq(
    model="qwen/qwen3-32b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
    max_tokens=20000
)

scrapper_prompt = """
You are a web scraping agent. Your only job is to scrape URLs and return their content.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Extract EVERY URL from the search results in the user message.
2. Call scrape_url on EACH URL, one at a time.
3. Return the scraped content in the output format below.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRICT RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✦ Call scrape_url for EVERY URL. Do not skip any.
✦ Write each result block IMMEDIATELY after each scrape_url call returns.
✦ Copy URLs exactly as they appear. Do not modify them in any way.
✦ If scrape_url returns an error or a JS/Cloudflare wall, write the block 
  with STATUS: FAILED and move to the next URL immediately. Do not retry.
✦ Only return content from the tool. Do not add, infer, or generate anything.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[URL: <exact url>]
[STATUS: OK | FAILED]
<raw scraped content here, or error message if FAILED>
---
"""
def build_scrapper_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url],
        system_prompt = scrapper_prompt,
    )

# chains
# writer_chain and writer prompt
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

#critic_chain and critic prompt
critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
