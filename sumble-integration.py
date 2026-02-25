# This script demonstrates how Sumble acts as the "Trigger" for the JigsawStack Engine
# NOTE: This is a proof-of-concept (POC) implementation. 
# Sumble API calls are currently mocked and untested in a live production environment.
# Updated to use python-dotenv for secure local development
import requests
import os
from dotenv import load_dotenv # Run: pip install python-dotenv

# Load variables from .env file
load_dotenv()

SUMBLE_API_KEY = os.getenv("SUMBLE_API_KEY")
JIGSAW_API_KEY = os.getenv("JIGSAW_API_KEY")

def trigger_gtm_pipeline():
    """
    Stage 0: Use Sumble to find companies with 'Active Intent'
    Signals: Hiring for OCR Engineers, Data Migration Projects, or 
    high-volume document processing infrastructure.
    """
    
    # 🛡️ SECURITY CHECK
    if not SUMBLE_API_KEY or not JIGSAW_API_KEY:
        print("❌ Error: API keys not found in environment variables.")
        print("Ensure you have a .env file with SUMBLE_API_KEY and JIGSAW_API_KEY.")
        return

    # 1. Query Sumble's Knowledge Graph for high-intent accounts
    # Example: Companies in Series B+ hiring for 'LLM Ops' or 'Document AI'
    sumble_query = {
        "intent_signals": ["hiring_ocr", "cloud_migration_active"],
        "industry": "FinTech",
        "employee_count": {"min": 50, "max": 500}
    }
    
    # sumble_response = requests.post("https://api.sumble.com/v1/intent", json=sumble_query)
    # target_companies = sumble_response.json()['companies']
    
    # Mock data for demonstration
    target_companies = ["AcmeFin", "SecureLoan", "GlobalPay"]

    for company in target_companies:
        print(f"🚀 Sumble detected intent at {company}. Passing to JigsawStack...")
        
        # 2. Hand off to your existing JigsawStack Harvester
        # Instead of searching all of HN, we search HN specifically for these domains
        # or key employees from these companies to find technical friction.
        
        search_query = f"{company} site:news.ycombinator.com"
        
        # This is where your 'intent-harvester.py' takes over
        # results = harvest_hn_mentions(search_query) 
        # ... proceed to Sentiment Chain and Scorer ...

if __name__ == "__main__":
    trigger_gtm_pipeline()