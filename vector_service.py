from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
import os
import time

class VectorService:
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = "market-data"
        
        
        if index_name not in [idx.name for idx in self.pc.list_indexes()]:
            self.pc.create_index(
                name=index_name, dimension=384, metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            while not self.pc.describe_index(index_name).status['ready']:
                time.sleep(1)
        
        self.index = self.pc.Index(index_name)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def find_internal_knowledge(self, description):
        try:
            query_vector = self.embeddings.embed_query(description)
            results = self.index.query(vector=query_vector, top_k=3, include_metadata=True)
            
            context = ""
            for res in results['matches']:
                meta = res['metadata']
                context += f"Internal Log: {meta.get('name')} | {meta.get('features')} | Price: {meta.get('price')}\n"
            return context if context else "No matching local records found."
        except Exception as e:
            print(f"Pinecone Search Error: {e}")
            return "Internal Vector Search is currently unavailable."