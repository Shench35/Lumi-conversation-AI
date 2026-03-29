import chromadb

client = chromadb.PersistentClient(path="./db")
collection = client.get_or_create_collection("docs")


def to_embeding(clean_text_result: str, keyword: str):
    try:
        collection.add(documents=[clean_text_result], ids=[keyword])
        print("Embedding stored in Chroma")
    except Exception as e:
        collection.update(documents=[clean_text_result], ids=[keyword])
        print(f"Embedding updated in Chroma: {e}")