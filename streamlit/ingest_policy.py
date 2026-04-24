from dotenv import load_dotenv
load_dotenv()

import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec


PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
INDEX_NAME = "policy-index"

def ingest():
    # Load the policy document
    loader = Docx2txtLoader("../Generic E-Commerce Company_ Master Policy Compendium.docx")
    documents = loader.load()
    print(f"Loaded document with {len(documents)} pages")

    # Chunk it
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    # Initialize Pinecone client directly
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)

    # Embed and push using the index directly
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    
    vectorstore = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )
    vectorstore.add_documents(chunks)
    print(f"Successfully uploaded {len(chunks)} chunks to Pinecone")

if __name__ == "__main__":
    ingest()