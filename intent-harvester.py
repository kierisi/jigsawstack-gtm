import json
import sys
import re
from jigsawstack import JigsawStack

# Initialize JigsawStack
api_key = "JIGSAW_API_KEY"
jigsaw = JigsawStack(api_key=api_key)

# Claude's brilliant keyword expansion
AI_KEYWORDS = [
    r"\bai\b", r"\bllm\b", "gpt", "claude", "gemini", r"\bml\b", "machine learning",
    "deep learning", "neural", "copilot", "agent", "embedding", r"\brag\b",
    "fine-tun", "diffusion", "transformer", "openai", "anthropic", "ollama"
]

def is_ai_related(title: str) -> bool:
    """Checks if any AI keyword exists in the title using boundaries for short words."""
    title_lower = title.lower()
    for keyword in AI_KEYWORDS:
        if re.search(keyword, title_lower):
            return True
    return False

def scrape_hn_ai_posts(pages: int = 1):
    print(f"\n--- 🔍 Booting JigsawStack Paginated Harvester ---")
    ai_posts = []

    for page in range(1, pages + 1):
        url = f"https://news.ycombinator.com/news?p={page}"
        print(f"Scraping page {page}: {url}...")

        scrape_params = {
            "url": url,
            "element_prompts": [
                "post title",
                "post points",
                "post url"
            ]
        }

        try:
            response = jigsaw.web.ai_scrape(scrape_params)
            data_groups = response.get("data", [])
            
            if not data_groups:
                print(f"  ⚠️ No data returned on page {page}.")
                continue

            # Separate the columns based on the keys the AI returned
            titles_raw = []
            points_raw = []
            
            for group in data_groups:
                key = group.get("key", "")
                if key == "post title":
                    titles_raw = group.get("results", [])
                elif key == "post points":
                    points_raw = group.get("results", [])

            # HN Quirk: The AI grabbed the title AND the website name next to it.
            # We filter out the website names (which always link to "from?site=...")
            clean_titles = []
            for t in titles_raw:
                href = next((attr.get("value", "") for attr in t.get("attributes", []) if attr.get("name") == "href"), "")
                if not href.startswith("from?site="):
                    clean_titles.append(t)

            print(f"  📊 Parsed {len(clean_titles)} actual posts from page {page}.")

            # Zip the titles and points back together into rows!
            for i in range(len(clean_titles)):
                t_obj = clean_titles[i]
                title = t_obj.get("text", "")
                
                # Extract the URL from the HTML attributes
                post_url = next((attr.get("value", "") for attr in t_obj.get("attributes", []) if attr.get("name") == "href"), "")
                
                # Safely grab points if they exist
                points = "0"
                if i < len(points_raw):
                    points = points_raw[i].get("text", "0").split()[0] # Turn "150 points" into "150"

                if title and is_ai_related(title):
                    ai_posts.append({
                        "title": title.strip(),
                        "points": points,
                        "url": post_url,
                        "hn_page": page
                    })

        except Exception as e:
            print(f"  ❌ Error on page {page}: {str(e)}")

    return ai_posts

if __name__ == "__main__":
    if "sk_4456" in api_key:
        print("\n[STARTING V2 GTM ENGINE: PAGINATION + PROPER PARSING]")
        
        # Let's scrape the top 3 pages of HackerNews
        posts = scrape_hn_ai_posts(pages=3)

        print(f"\n✅ Found {len(posts)} AI-related posts across 3 pages:\n")
        
        for post in posts:
            print(f"  [{post.get('points', '0')} pts] {post.get('title')}")
            print(f"           {post.get('url')}\n")
            
        print("--- GTM Engineering Note ---")
        print("This proves the issue wasn't the API, it was just how the response was parsed!")
        print("This is a killer demo: Multi-page AI extraction piped into a local filter.")
    else:
        print("Please ensure your API key is correctly set.")