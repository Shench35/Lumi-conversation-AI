import ollama
import re
from sklearn.feature_extraction.text import TfidfVectorizer  # or just use simple extraction


client = ollama.Client(host="http://127.0.0.1:11434")



# def keyword_getter(prompt: str) -> str:
#     keyword = client.generate(
#         model="tinyllama",
#         prompt=f"Extract the main topic from this question as a single keyword or short phrase. Return ONLY the keyword, nothing else, no punctuation, no explanation.\n\nQuestion: {prompt}\nKeyword:"
#     )
    
#     raw = keyword["response"].strip()
#     first_line = raw.split('\n')[0].strip()
#     cleaned = re.sub(r'["\'\.\,\:\;\!\?]', '', first_line).strip()
    
#     # Remove common prefixes TinyLlama adds
#     for prefix in ["Keyword:", "keyword:", "Keyword -", "Topic:", "Answer:"]:
#         if cleaned.startswith(prefix):
#             cleaned = cleaned[len(prefix):].strip()
    
#     words = cleaned.split()
#     if len(words) > 3:
#         cleaned = ' '.join(words[:3])
    
#     return cleaned.replace(' ', '_')



def keyword_getter(prompt: str) -> str:
    # Simple extraction - take the most important words, no LLM needed
    stop_words = {'what', 'is', 'are', 'how', 'why', 'when', 'where', 'who', 
                  'does', 'do', 'the', 'a', 'an', 'in', 'of', 'to', 'and', 
                  'or', 'tell', 'me', 'about', 'explain', 'describe'}
    words = re.sub(r'[^\w\s]', '', prompt.lower()).split()
    keywords = [w for w in words if w not in stop_words]
    return '_'.join(keywords[:2]) if keywords else prompt.split()[0]