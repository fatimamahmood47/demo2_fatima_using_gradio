from pinecone import Pinecone
PINECONE_API_KEY  = "pcsk_71wCna_Jq2J1KhinJrrskA3Xs3JM81kJsP8imnS6W7Tjo3L3B8E8Xdx3Jzqe4f4VKJsM95"
PINECONE_INDEX_NAME = "myindex"

pc = Pinecone(api_key= PINECONE_API_KEY)
idx = pc.Index(PINECONE_INDEX_NAME)



print(idx.describe_index_stats())  # should show a non-zero vector count

