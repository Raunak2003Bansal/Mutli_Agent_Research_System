from agents import writer_agent , critic_chain
from tools import ResearchReport


def run_research_pipeline(topic : str) -> str:
    result = writer_agent.invoke({"messages": [("user", topic)]})
    report: ResearchReport = result["structured_response"]
    return result

def audit_scraping_tools(result):
    messages = result.get("messages", [])
    
    print("\n" + "="*60)
    print(" 🔍 TOOL EXECUTION AUDIT: SCRAPE STATUS")
    print("="*60 + "\n")
    
    # Step 1: Map the unique tool call IDs to the URLs the model requested
    url_map = {}
    for msg in messages:
        # Check if the AI requested any tool calls
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call.get("name") == "scrape_url":
                    url_map[tool_call["id"]] = tool_call["args"].get("url")
    
    # Step 2: Correlate those IDs to the actual tool execution outputs
    scrape_attempts = 0
    for msg in messages:
        # Identify messages coming back from a tool
        if msg.__class__.__name__ == "ToolMessage" and msg.name == "scrape_url":
            scrape_attempts += 1
            url = url_map.get(msg.tool_call_id, "Unknown URL")
            content_lower = msg.content.lower()
            
            # Catch known soft-failure indicators from news walls
            failure_indicators = [
                "please enable js", 
                "disable any ad blocker", 
                "forbidden", 
                "captcha detected",
                "403 error"
            ]
            
            is_failed = any(err in content_lower for err in failure_indicators)
            
            if is_failed:
                print(f"❌ FAILED TO SCRAPE: {url}")
                # Print the first line of the error block as the reason
                reason = msg.content.strip().split('\n')[0][:90]
                print(f"   Reason: \"{reason}...\"")
            else:
                print(f"✅ SUCCESSFULLY SCRAPED: {url}")
                # Print a small preview slice of the actual text grabbed
                preview = msg.content.strip().replace('\n', ' ')[:90]
                print(f"   Data Sneak-Peek: \"{preview}...\"")
                
            print("-" * 50)
            
    if scrape_attempts == 0:
        print("ℹ️ No scrape operations were attempted during this run.")
        
    print("\n" + "="*60)


def print_beautiful_report(result):
    # 1. Extract the structured Pydantic report object from the dictionary
    report = result.get("structured_response")
    
    if not report:
        print("❌ No structured report found in the response.")
        return

    # 2. Print the content using clean Markdown formatting
    print("\n" + "="*60)
    print(" 📜 FINAL RESEARCH REPORT")
    print("="*60 + "\n")
    
    print(f"## Introduction\n{report.introduction}\n")
    print("-" * 40 + "\n")
    
    print("## Key Findings\n")
    for idx, finding in enumerate(report.key_findings, 1):
        print(f"### {idx}. {finding.subheading}")
        print(f"{finding.explanation}\n")
        
    print("-" * 40 + "\n")
    print(f"## Conclusion\n{report.conclusion}\n")
    
    print("-" * 40 + "\n")
    print("## Sources Consulted:")
    for source in report.sources:
        print(f"🔗 {source}")
    print("\n" + "="*60)

if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    result = run_research_pipeline(topic)
    print_beautiful_report(result)
    audit_scraping_tools(result)
