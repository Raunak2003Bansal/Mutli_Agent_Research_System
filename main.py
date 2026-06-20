from utils.pydantic_output import ResearchReport
from utils.agents import run_scraping_pipeline, writer_chain

def run_research_pipeline(topic : str) -> str:
    content = run_scraping_pipeline(topic)
    result = writer_chain.invoke({"topic": topic, "scraped_content": content})
    return result

def print_report(report: ResearchReport):
    print("\n" + "="*60)
    print(" 📜 FINAL RESEARCH REPORT")
    print("="*60 + "\n")
    
    print("## Introduction")
    print(report.introduction)
    print("\n" + "-"*40 + "\n")

    print("## Key Findings\n")
    for idx, finding in enumerate(report.key_findings, 1):
        print(f"### {idx}. {finding.subheading}")
        print(finding.explanation)
        print()

    print("-"*40 + "\n")

    print("## Conclusion")
    print(report.conclusion)
    print("\n" + "-"*40 + "\n")

    print("## Sources Consulted")
    for source in report.sources:
        print(f"  🔗 {source}")

    print("\n" + "="*60)





if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    result = run_research_pipeline(topic)
    print_report(result)
    
