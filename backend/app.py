import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles  # ← Import StaticFiles
from fastapi.templating import Jinja2Templates
from utils.agents import run_scraping_pipeline, writer_chain
from utils.pydantic_output import ResearchReport

# Establish paths dynamically relative to this file's position
BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "../templates"))

app = FastAPI()

# Mount the static directory to serve your CSS and JS
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "../static")), name="static")

def format_report(report: ResearchReport) -> str:
    lines = []
    lines.append("\n" + "="*60)
    lines.append(" 📜 FINAL RESEARCH REPORT")
    lines.append("="*60 + "\n")
    
    lines.append("## Introduction")
    lines.append(report.introduction)
    lines.append("\n" + "-"*40 + "\n")

    lines.append("## Key Findings\n")
    for idx, finding in enumerate(report.key_findings, 1):
        lines.append(f"### {idx}. {finding.subheading}")
        lines.append(finding.explanation)
        lines.append("")

    lines.append("-"*40 + "\n")

    lines.append("## Conclusion")
    lines.append(report.conclusion)
    lines.append("\n" + "-"*40 + "\n")

    lines.append("## Sources Consulted")
    for source in report.sources:
        lines.append(f"  🔗 {source}")

    lines.append("\n" + "="*60)
    return "\n".join(lines)

def run_research_pipeline(topic: str) -> str:
    content = run_scraping_pipeline(topic)
    result = writer_chain.invoke({"topic": topic, "scraped_content": content})
    return result

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/submit")
async def submit(request: Request):
    body = await request.json()
    topic = body.get("topic")

    if not topic or not topic.strip():
        return {"error": "Topic cannot be empty"}

    result = run_research_pipeline(topic)
    if result is None:
        return {"error": "Could not generate report. Try a different topic."}
    
    result_str = format_report(result)
    return {"message": result_str}