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
        
        for group in data:
            key = group.get("key", "").lower()
            results = group.get("results", [])
            if not results: continue
            
            if "url" in key or "link" in key:
                t_obj = results[0]
                href = next((attr.get("value", "") for attr in t_obj.get("attributes", []) if attr.get("name") == "href"), "")
                if href: 
                    thread_url = href
                elif "http" in t_obj.get("text", "") or "item?id=" in t_obj.get("text", ""): 
                    thread_url = t_obj.get("text")
            elif "title" in key:
                title = results[0].get("text", "")
                
        if thread_url:
            if thread_url.startswith("item?id="):
                thread_url = f"https://news.ycombinator.com/{thread_url}"
            print(f"✅ Found Thread: '{title}'")
            print(f"🔗 URL: {thread_url}")
            return thread_url
        else:
            print("⚠️ Could not extract a valid thread URL. Falling back to default.")
            return "https://news.ycombinator.com/item?id=38006356" 
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return "https://news.ycombinator.com/item?id=38006356"

def score_thread_comments(thread_url):
    """STEP 2: Scrapes the thread and uses the SENTIMENT API to evaluate frustration."""
    print(f"\n--- 🧠 STEP 2: Intent Extraction & Sentiment Analysis ---")
    print(f"Extracting comments from thread...")

    # FIX: Stripped down to the absolute most basic semantic words.
    # We let the AI figure out what a "username" and "comment" are.
    scrape_params = {
        "url": thread_url,
        "element_prompts": [
            "username",
            "comment"
        ]
    }

    try:
        response = jigsaw.web.ai_scrape(scrape_params)
        data_groups = response.get("data", [])
        
        if not data_groups:
            print("  ⚠️ No comments returned. Thread might be empty.")
            return []

        authors_raw, texts_raw = [], []
        
        for group in data_groups:
            key = group.get("key", "").lower()
            if "user" in key or "author" in key:
                authors_raw = group.get("results", [])
            elif "comment" in key or "text" in key:
                texts_raw = group.get("results", [])

        print(f"  📊 AI extracted {len(texts_raw)} comments. Routing to Sentiment API...")

        scored_leads = []
        
        # Determine how many we actually have to loop through
        loop_count = min(len(texts_raw), 15)
        
        for i in range(loop_count):
            text = texts_raw[i].get("text", "")
            author = authors_raw[i].get("text", "Unknown") if i < len(authors_raw) else "Unknown"

            if len(text) > 40: # Filter out tiny comments
                print(f"  🔍 Analyzing emotion for {author}...")
                
                frustration_score = 0
                emotion_label = "Neutral"
                
                try:
                    # Truncate to 800 chars for API safety
                    safe_text = text[:800]
                    sentiment_response = jigsaw.sentiment({"text": safe_text})
                    
                    sentiment_type = sentiment_response.get("sentiment", "neutral")
                    emotion = sentiment_response.get("emotion", "none")
                    raw_score = sentiment_response.get("score", 0.0)
                    
                    emotion_label = emotion.capitalize()
                    
                    # Convert float to a 1-10 scale. Emphasize negative emotions.
                    if sentiment_type == "negative" or emotion in ["anger", "frustration", "sadness", "disgust"]:
                        frustration_score = int(raw_score * 10)
                    else:
                        frustration_score = 1
                        
                except Exception as e:
                    print(f"    ⚠️ Sentiment API error: {e}")

                # BUILDING THE ENRICHED USER PROFILE
                hn_profile = f"https://news.ycombinator.com/user?id={author.strip()}"
                github_search = f"https://github.com/search?q={author.strip()}&type=users"
                
                # Clean up the preview so it prints beautifully
                preview = text[:120].strip().replace("\n", " ")
                if len(text) > 120: preview += "..."

                scored_leads.append({
                    "author": author.strip(),
                    "score": frustration_score,
                    "emotion": emotion_label,
                    "hn_profile": hn_profile,
                    "github_search": github_search,
                    "comment_preview": preview
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
        
    user_input = sys.argv[1] if len(sys.argv) > 1 else "PDF parsing OCR"
    
    print("[STARTING V8 GTM ENGINE: THE 'KEEP IT SIMPLE' PIPELINE]")
    
    if user_input.startswith("http://") or user_input.startswith("https://"):
        print(f"\n--- 🔗 Direct URL Mode ---")
        found_url = user_input
    else:
        found_url = auto_find_thread(user_input)
    
    leads = score_thread_comments(found_url)

    print("\n[PIPELINE COMPLETE: HIGH-INTENT LEADS DETECTED]")
    
    if leads:
        # Dynamically print the correct number of leads based on what we actually scored
        display_count = min(len(leads), 5)
        print(f"\n🚨 Top {display_count} prospects from this thread:\n")
        
        for lead in leads[:display_count]: 
            # Add a visual indicator for highly frustrated users
            alert = "🔥 HIGH FRICTION" if lead['score'] >= 5 else "ℹ️ NEUTRAL/POSITIVE"
            
            print(f"👤 USER: {lead['author']} | {alert} (Score: {lead['score']}/10 | Emotion: {lead['emotion']})")
            print(f"   🔗 HN Profile: {lead['hn_profile']}")
            print(f"   🐙 GitHub Recon: {lead['github_search']}")
            print(f"   💬 Preview: \"{lead['comment_preview']}\"")
            print("-" * 75)
    else:
        print("\n✅ No valid comments extracted from this thread.")
        
    print("\n--- GTM Engineering Note ---")
    print("Lesson learned: Over-prompting breaks the semantic reasoning of the AI Scraper.")
    print("Keeping prompts broad ('username', 'comment') yields the best extraction stability.")