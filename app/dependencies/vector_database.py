# embeddings and vector database 
from openai import OpenAI
from pinecone import Pinecone 

# data types 
from typing import List

# load api keys 
from dotenv import load_dotenv
import os

# out
import json

# get api keys 
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

class QueryProductNames:
    def __init__(self): 
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pinecone_client.Index(PINECONE_INDEX_NAME) 

    def _create_embeddings(self, external_product_name: str) -> List[float]:
        set_dimension = 1536
        response = self.openai_client.embeddings.create(
            input=[external_product_name],
            model="text-embedding-3-small",
            dimensions = set_dimension 
        )
        return response.data[0].embedding

    def _query_pinecone(self, vector: List[float] ) -> List[str]:
        number_returns = 10 
        result = self.index.query(
            vector=vector,
            top_k=number_returns, 
            include_metadata=True
        )
        return result 
    
    def query_product_names(self, external_product_name :str ) -> List[str]: 
        query_embedding = self._create_embeddings(external_product_name)
        return self._query_pinecone(query_embedding)
 
 
# # sample usage 
# q_inst = QueryProductNames() 
# result = q_inst.query_product_names("VE22硬質ビニル電線管(4m)ベージュ") 
# print(result)