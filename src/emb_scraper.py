from requests import session
from scrapling.fetchers import FetcherSession
import re

def scrape_wikipedia(keyword: str) -> dict:
    
    # Format keyword for Wikipedia URL
    search_term = keyword.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{search_term}"
    
    with FetcherSession(impersonate="chrome") as session:
        page = session.get(url, stealthy_headers=True)

    
    # Get the title
    title = page.find("h1", id="firstHeading").text
    
    # Get all paragraphs from the main content
    content_div = page.find("div", id="mw-content-text")
    paragraphs = content_div.find_all("p")
    
    # Clean and join text
    text = "\n\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
    
    return {
        "title": title,
        "url": url,
        "text": text
    }


def clean_text(text: str) -> str:
    text = re.sub(r'\[\d+\]', '', text)  # Remove citations [1], [2]
    text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
    return text.strip()
