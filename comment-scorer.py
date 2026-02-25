import json
import sys
import urllib.parse
from jigsawstack import JigsawStack

# Initialize JigsawStack
api_key = "JIGSAW_API_KEY"
jigsaw = JigsawStack(api_key=api_key)

def auto_find_thread(topic):
    """STEP 1: Autonomously searches HN for the top thread matching the topic."""
    print(f"\n--- 🕵️ STEP 1: Autonomous Prospecting ---")
    print(f"Searching HackerNews for the top discussion on: '{topic}'")
    
    # We query HN's Algolia search engine directly
    search_url = f"https://hn.algolia.com/?q={urllib.parse.quote(topic)}"
    
    try:
        response = jigsaw.web.ai_scrape({
            "url": search_url,
            "element_prompts": [
                "title of the first search result",
                "hacker news comments url for the first result"
            ]
        })
        
        data = response.get("data", [])
        thread_url = None
        title = "Unknown Thread"
        
        # Fuzzy match to find the URL and Title in the AI's response
        for group in data:
            key = group.get("key", "").lower()
            results = group.get("results", [])
            if not results: continue
            
            if "url" in key or "link" in key:
                t_obj = results[0]
                # Try to get the actual href attribute first
                href = next((attr.get("value", "") for attr in t_obj.get("attributes", []) if attr.get("name") == "href"), "")
                if href: 
                    thread_url = href
                # Fallback to the text if the AI returned the raw URL string
                elif "http" in t_obj.get("text", "") or "item?id=" in t_obj.get("text", ""): 
                    thread_url = t_obj.get("text")
            elif "title" in key:
                title = results[0].get("text", "")
                
        if thread_url:
            # Normalize relative Algolia URLs to full HN links
            if thread_url.startswith("item?id="):
                thread_url = f"https://news.ycombinator.com/{thread_url}"
            print(f"✅ Found Thread: '{title}'")
            print(f"🔗 URL: {thread_url}")
            return thread_url
        else:
            print("⚠️ Could not extract a valid thread URL. Falling back to default OCR thread.")
            return "https://news.ycombinator.com/item?id=38006356" # Fallback PDF thread
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return "https://news.ycombinator.com/item?id=38006356"

def score_thread_comments(thread_url):
    """STEP 2: Scrapes the provided thread and evaluates developer frustration."""
    print(f"\n--- 🧠 STEP 2: Deep Intent Scoring ---")
    print(f"Diving into thread comments...")

    # FIX: Asking for "lists" forces the AI to grab every comment, not just the first one.
    scrape_params = {
        "url": thread_url,
        "element_prompts": [
            "list of all comment authors",
            "list of all comment texts",
            "list of developer pain points", 
            "list of frustration scores 1 to 10"      
        ]
    }

    try:
        response = jigsaw.web.ai_scrape(scrape_params)
        data_groups = response.get("data", [])
        
        if not data_groups:
            print("  ⚠️ No comments returned. Thread might be empty.")
            return []

        authors_raw, texts_raw, pain_points_raw, scores_raw = [], [], [], []
        
        # FIX: Fuzzy key matching so we don't break if the AI changes the key name slightly
        for group in data_groups:
            key = group.get("key", "").lower()
            if "author" in key:
                authors_raw = group.get("results", [])
            elif "text" in key or "bod" in key:
                texts_raw = group.get("results", [])
            elif "pain" in key:
                pain_points_raw = group.get("results", [])
            elif "score" in key:
                scores_raw = group.get("results", [])

        print(f"  📊 AI extracted {len(texts_raw)} comments to evaluate.")

        scored_leads = []
        for i in range(len(texts_raw)):
            text = texts_raw[i].get("text", "")
            author = authors_raw[i].get("text", "Unknown") if i < len(authors_raw) else "Unknown"
            pain = pain_points_raw[i].get("text", "None identified") if i < len(pain_points_raw) else "None identified"
            
            # Extract just the number
            raw_score = scores_raw[i].get("text", "0") if i < len(scores_raw) else "0"
            clean_score = ''.join(filter(str.isdigit, raw_score))
            score_val = int(clean_score) if clean_score else 0

            if len(text) > 30: # Filter out tiny "I agree" comments
                scored_leads.append({
                    "author": author.strip(),
                    "score": score_val,
                    "pain_point": pain.strip(),
                    "comment_preview": text[:100].strip().replace("\n", " ") + "..."
                })

        # Sort highest frustration to the top
        scored_leads.sort(key=lambda x: x["score"], reverse=True)
        return scored_leads

    except Exception as e:
        print(f"  ❌ Error evaluating thread: {str(e)}")
        return []

if __name__ == "__main__":
    if "sk_4456" not in api_key:
        print("Please ensure your API key is correctly set.")
        sys.exit()
        
    # Allow passing a custom topic OR a direct URL via terminal
    user_input = sys.argv[1] if len(sys.argv) > 1 else "PDF parsing OCR"
    
    print("[STARTING V3 GTM ENGINE: END-TO-END AUTONOMOUS PIPELINE]")
    
    # Check if the user passed a URL directly
    if user_input.startswith("http://") or user_input.startswith("https://"):
        print(f"\n--- 🔗 Direct URL Mode ---")
        print(f"Bypassing search. Using provided URL: {user_input}")
        found_url = user_input
    else:
        # Run Step 1 (Search)
        found_url = auto_find_thread(user_input)
    
    # Run Step 2 (Score)
    leads = score_thread_comments(found_url)

    print("\n[PIPELINE COMPLETE: HIGH-INTENT LEADS DETECTED]")
    
    # Filter for highly frustrated users (Score > 6)
    high_intent = [lead for lead in leads if lead["score"] > 6]
    
    if high_intent:
        print(f"\n🚨 Found {len(high_intent)} developers experiencing high friction:\n")
        for lead in high_intent[:5]: # Show top 5
            print(f"👤 {lead['author']} (Frustration: {lead['score']}/10)")
            print(f"🔥 Pain Point: {lead['pain_point']}")
            print(f"💬 \"{lead['comment_preview']}\"\n")
    else:
        print("\n✅ No highly frustrated users found in this thread.")
        
    print("--- GTM Engineering Note ---")
    print("Zero manual bottleneck. The pipeline searched, found, scraped, and scored entirely on its own.")