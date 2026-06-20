from pydantic import BaseModel, Field
from typing import List


class various_search_queries(BaseModel):
    query1: str = Field(description="A semantically different variation of the original search query, ideally targeting different sources or using different phrasing.")
    query2: str = Field(description="Another semantically different variation of the original search query.")
    query3: str = Field(description="A third semantically different variation of the original search query.")

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