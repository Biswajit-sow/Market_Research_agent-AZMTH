import os
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("market-data")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def seed_database():
    print("Seeding internal Pinecone database...")
    
    knowledge_base = [
        {"id": "kb1", "text": "HydroSmart: Premium AI bottle, $79, LED sensors", "meta": {"name": "HydroSmart", "price": "$79", "features": "LED"}},
        {"id": "kb2", "text": "AquaTech Pro: Rugged hydration, $120, GPS tracking", "meta": {"name": "AquaTech Pro", "price": "$120", "features": "GPS"}},
        {"id": "kb3", "text": "WaterLogic: Budget bottle, $30, temperature LCD", "meta": {"name": "WaterLogic", "price": "$30", "features": "LCD"}},
    ]
    
    for item in knowledge_base:
        vec = embeddings.embed_query(item["text"])
        index.upsert(vectors=[(item["id"], vec, item["meta"])])
    
    print("Database seeding successful.")

if __name__ == "__main__":
    seed_database()