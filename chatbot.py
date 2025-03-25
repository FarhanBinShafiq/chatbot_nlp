import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from urllib.parse import urljoin, urlparse
import time

# Load a more precise pre-trained question-answering model
qa_model = pipeline("question-answering", model="roberta-base-squad2")

# Store pages as raw text
pages = {}

def crawl_website(base_url, max_pages=10, timeout=10):
    """Crawl the website starting from base_url and store content."""
    global pages
    pages.clear()
    visited = set()
    to_visit = [base_url]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Exclude chatbot UI text
            chatbot_div = soup.find(id="chatbot")
            if chatbot_div:
                chatbot_div.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            pages[url] = text
            print(f"Crawled {url}: {text[:200]}...")
            
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(base_url, link['href'])
                if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                    if absolute_url not in visited and absolute_url not in to_visit:
                        to_visit.append(absolute_url)
            
            visited.add(url)
            time.sleep(1)
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    
    print(f"Total crawled pages: {len(pages)}. URLs: {list(pages.keys())}")
    return None

def search(query_str, _):
    """Use AI to answer the query, returning only the best result."""
    best_result = None
    best_score = 0.0
    
    # Rephrase for specificity if not a question
    if not query_str.strip().endswith('?'):
        if "number" in query_str.lower():
            query_str = f"What is the {query_str}?"
        elif "email" in query_str.lower():
            query_str = f"What is the {query_str} address?"
        else:
            query_str = f"Who or what is {query_str}?"
    
    for url, content in pages.items():
        try:
            result = qa_model(question=query_str, context=content)
            print(f"Query: {query_str}, URL: {url}, Score: {result['score']}, Answer: {result['answer']}, Context snippet: {content[:200]}...")
            if result['score'] > best_score and result['score'] > 0.3:  # Threshold 0.3
                best_score = result['score']
                answer = result['answer']
                best_result = (url, answer)
        except Exception as e:
            print(f"Error processing {url}: {e}")
    
    if best_result:
        print(f"Best result selected: {best_result}")
    else:
        print("No result above threshold found.")
    return [best_result] if best_result else [("No URL", "I couldn’t find an answer on this site.")]

def index_website(base_url):
    return crawl_website(base_url)