from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from utils.pydantic_output import ResearchReport, various_search_queries


query_parser = PydanticOutputParser(pydantic_object=various_search_queries)

question_variation_prompt = PromptTemplate(
    input_variables=["topic"],
    template="""Generate 3 semantic search query variations for the following topic.

Topic: '{topic}'

Rules:
- Each query must be specific enough to return individual news articles, not topic index pages
- Add qualifiers like 'latest', 'update', 'report', 'explained', or current year(note current year is 2026) to make the queries more specific.
- Avoid overly broad queries that return category/hub pages

{format_instructions}""",
    partial_variables={"format_instructions": query_parser.get_format_instructions()}
)


parser = PydanticOutputParser(pydantic_object=ResearchReport)

summarizer_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an Expert Research Analyst and Report Writer.
You will be given scraped content from multiple web sources, each labeled with its source URL.
Your job is to synthesize this information into a professional, structured research report.

### Instructions
- Base your report STRICTLY on the provided source content.
- Ignore navigation menus, cookie notices, or website boilerplate.
- Write subheadings as plain text only — no markdown, no asterisks, no bold formatting.
- Write in a professional, analytical, and objective tone.
- For each key finding, include at least one specific statistic, company name, product name, or direct data point from the sources. Avoid vague generalizations like 'AI will improve things'.
- Ensure the example or statistic used in each finding directly supports that finding's subheading. Do not use unrelated facts as evidence.
- Current year is 2026. If the sources mention trends or predictions, evaluate them based on the current year and include that analysis in the conclusion. Do not use content older than 2026.

{format_instructions}"""),
    ("human", """Research Topic: {topic}

Source Content:
{scraped_content}

Generate a comprehensive research report based strictly on the source content above.""")
]).partial(format_instructions=parser.get_format_instructions())

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