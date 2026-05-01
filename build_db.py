import chromadb

def build_vector_db():
    print("🚀 Initializing Vector Database Build...")
    
    # 1. Create a local folder to store the database
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # 2. Create a "collection" (like a table in SQL)
    # We use get_or_create so we don't get an error if we run this twice
    collection = client.get_or_create_collection(name="compliance_policy")
    
    # 3. Read our text file
    with open("policy.txt", "r") as file:
        policy_text = file.read()
        
    # 4. Chunk the text (splitting by the numbered sections for simplicity)
    chunks = policy_text.split("\n\n")
    
    # 5. Insert the chunks into the Vector Database
    for i, chunk in enumerate(chunks):
        if chunk.strip() == "": continue
        
        # ChromaDB automatically converts the text into vector embeddings here!
        collection.add(
            documents=[chunk],
            metadatas=[{"source": "razorpay_policy.txt", "section": str(i)}],
            ids=[f"chunk_{i}"]
        )
        print(f"✅ Embedded and stored chunk {i}")

    print("🎉 Database successfully built in the './chroma_db' folder!")

if __name__ == "__main__":
    build_vector_db()