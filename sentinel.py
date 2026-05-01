import os
import requests
from bs4 import BeautifulSoup
from typing import TypedDict, List
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
import chromadb # <-- NEW: Vector DB Import


os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"

llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0)


class SentinelState(TypedDict):
    url: str
    scraped_text: str
    retrieved_policy: str  
    compliance_flags: List[str]
    risk_score: float
    summary: str
    final_decision: str

class ComplianceExtraction(BaseModel):
    is_high_risk: bool = Field(description="True if the business mentions crypto, gambling, adult services, pirated/cracked software, copyright infringement, or guaranteed high returns.")
    business_category: str = Field(description="The industry of the business, e.g., 'Bakery', 'Crypto Exchange', 'Software Distribution'.")
    flagged_keywords: List[str] = Field(description="Any suspicious words found in the text.")


def scraper_agent(state: SentinelState):
    url = state['url']
    print(f"\n [Scraper Agent]: Fetching LIVE data from {url}...")
    
    if state.get('scraped_text') and state['scraped_text'].strip() != "":
        print("   -> Using manual text override from dashboard.")
        return {"scraped_text": state['scraped_text']}
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.extract()
            
        clean_text = soup.get_text(separator=' ', strip=True)
        clean_text = clean_text[:5000] 
        
        print(f"   -> Success! Scraped {len(clean_text)} characters.")
        return {"scraped_text": clean_text}
        
    except Exception as e:
        print(f"   ->  Scraper Failed: {e}")
        return {"scraped_text": f"Error scraping website: {e}. The site might be blocking bots."}

def policy_retriever_agent(state: SentinelState):
    print("\n [Policy Retriever Agent]: Searching Corporate Policy...")
    
    try:
        
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection(name="compliance_policy")
        
        
        search_query = state['scraped_text'][:200] if state.get('scraped_text') else "prohibited business software cracked"
        
    
        results = collection.query(
            query_texts=[search_query],
            n_results=2 
        )
        
        retrieved_docs = "\n".join(results['documents'][0])
        print("   -> Success! Relevant policy rules retrieved.")
        return {"retrieved_policy": retrieved_docs}
        
    except Exception as e:
        print(f"   -> ⚠️ Retriever Failed: {e}")
        return {"retrieved_policy": "Error retrieving policy. Default to strict manual review."}

def compliance_agent(state: SentinelState):
    print("\n [Compliance Agent]: Analyzing against Policy...")
    
    structured_llm = llm.with_structured_output(ComplianceExtraction)
    
  
    prompt = f"""
    You are a strictly rule-bound Fintech Compliance Auditor.
    Evaluate the Website Text ONLY against the Corporate Policy provided below. 
    Do not use outside assumptions. If the site violates a Prohibited or High-Risk category in the policy, mark it as High Risk.
    
    CRITICAL RULE: If the text says the scraper failed, DO NOT automatically assume the site is safe. Use your internal knowledge of the URL. If the domain distributes cracked/pirated software, flag it immediately.
    
    --- CORPORATE POLICY ---
    {state.get('retrieved_policy', 'No specific policy found.')}
    
    --- WEBSITE TEXT ---
    {state['scraped_text']}
    """
    
    result = structured_llm.invoke(prompt)
    
    print(f"   -> Category: {result.business_category} | High Risk: {result.is_high_risk}")
    
    return {
        "compliance_flags": result.flagged_keywords,
        "risk_score": 0.9 if result.is_high_risk else 0.1 
    }

def risk_agent(state: SentinelState):
    print(f"\n [Risk Agent]: Evaluating risk score of {state['risk_score']}...")
    decision = "Reject (High Risk)" if state["risk_score"] > 0.7 else "Approve (Low Risk)"
    return {"final_decision": decision}

def synthesizer_agent(state: SentinelState):
    print("\n [Synthesizer Agent]: Drafting executive summary...")
    
    prompt = f"""
    Write a 2-sentence executive summary for a human reviewer.
    Business Category: {state.get('compliance_flags', 'None')}
    Decision: {state['final_decision']}
    Scraped Text: {state['scraped_text']}
    """
    
    summary_response = llm.invoke(prompt)
    
    raw_content = summary_response.content
    if isinstance(raw_content, list):
        clean_summary = raw_content[0].get('text', str(raw_content))
    else:
        clean_summary = raw_content
        
    return {"summary": clean_summary}


workflow = StateGraph(SentinelState)

# Add nodes
workflow.add_node("scraper", scraper_agent)
workflow.add_node("retriever", policy_retriever_agent) 
workflow.add_node("compliance", compliance_agent)
workflow.add_node("risk", risk_agent)
workflow.add_node("synthesizer", synthesizer_agent)

workflow.set_entry_point("scraper")
workflow.add_edge("scraper", "retriever")           
workflow.add_edge("retriever", "compliance")        
workflow.add_edge("compliance", "risk")
workflow.add_edge("risk", "synthesizer")
workflow.add_edge("synthesizer", END)


sentinel_engine = workflow.compile()


if __name__ == "__main__":
    print("\n🚀 --- SENTINEL ENGINE INITIALIZED ---\n")
    
   
    initial_state = {
        "url": "https://getintopc.com",
        "scraped_text": "",
        "retrieved_policy": "", 
        "compliance_flags": [],
        "risk_score": 0.0,
        "summary": "",
        "final_decision": ""
    }
    
    final_state = sentinel_engine.invoke(initial_state)
    
    print("\n====================================")
    print("        FINAL SENTINEL REPORT       ")
    print("====================================")
    print(f"Decision: {final_state['final_decision']}")
    print(f"Flags:    {final_state['compliance_flags']}")
    print(f"Summary:  {final_state['summary']}")
    print("====================================\n")