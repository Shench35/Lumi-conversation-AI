import chromadb

from src.emb_scraper import scrape_wikipedia, clean_text

client = chromadb.PersistentClient(path="./db")
collection = client.get_or_create_collection("docs")


def to_embeding(clean_text_result: str, keyword: str):
    with open("k8s.txt", "w") as f:
        f.write(clean_text_result)

    with open("k8s.txt", "r") as f:
        text = f.read()

        collection.add(documents=[text], ids=[keyword])

        print("Embedding stored in Chroma")
        print(text)
        print(collection)
