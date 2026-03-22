import ollama

client = ollama.Client(host="http://127.0.0.1:11434")

def keyword_getter(prompt:str) -> str:
        keyword = client.generate(
        model="tinyllama",
        prompt = f"Extract the main topic from this question as a single keyword or short phrase. Return ONLY the keyword, nothing else, no punctuation, no explanation.\n\nQuestion: {prompt}\nKeyword:"
        )
        return keyword["response"].strip()