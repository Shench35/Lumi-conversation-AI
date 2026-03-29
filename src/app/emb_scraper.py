from scrapling.fetchers import FetcherSession
import re

def scrape_wikipedia(keyword: str) -> dict:
    search_term = keyword.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{search_term}"
    
    with FetcherSession(impersonate="chrome") as session:
        page = session.get(url, stealthy_headers=True)

    # safe title extraction
    title_el = page.find("h1", id="firstHeading")
    title = title_el.text if title_el else keyword

    # safe content extraction
    content_div = page.find("div", id="mw-content-text")
    if not content_div:
        print(f"Could not find content div for: {url}")
        return {"title": title, "url": url, "text": ""}

    paragraphs = content_div.find_all("p")
    text = "\n\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
    
    print(f"Scraped text length: {len(text)}")
    return {"title": title, "url": url, "text": text}


def clean_text(text: str) -> str:
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()