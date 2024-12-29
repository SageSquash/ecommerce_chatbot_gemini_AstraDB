import os
from dotenv import load_dotenv
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import pandas as pd
from ecommbot.data_converter import dataconveter

# Load environment variables at the very beginning
load_dotenv(override=True)

def check_env_variables():
    required_vars = [
        "GOOGLE_API_KEY",
        "ASTRA_DB_API_ENDPOINT",
        "ASTRA_DB_APPLICATION_TOKEN",
        "ASTRA_DB_KEYSPACE"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please ensure these are set in your .env file"
        )

def ingestdata(status):
    # Check environment variables first
    check_env_variables()
    
    # Initialize Gemini embeddings
    try:
        embedding = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",  # Gemini embedding model
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    except Exception as e:
        raise Exception(f"Failed to initialize embeddings: {str(e)}")

    # Initialize AstraDB
    try:
        vstore = AstraDBVectorStore(
            embedding=embedding,
            collection_name="chatbotecomm",
            api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
            token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
            namespace=os.getenv("ASTRA_DB_KEYSPACE"),
        )
    except Exception as e:
        raise Exception(f"Failed to initialize AstraDB: {str(e)}")

    if status is None:
        try:
            docs = dataconveter()
            inserted_ids = vstore.add_documents(docs)
            return vstore, inserted_ids
        except Exception as e:
            raise Exception(f"Failed to ingest documents: {str(e)}")
    else:
        return vstore

if __name__ == '__main__':
    try:
        vstore, inserted_ids = ingestdata(None)
        print(f"\nInserted {len(inserted_ids)} documents.")
        
        results = vstore.similarity_search("can you tell me the low budget sound basshead.")
        for res in results:
            print(f"* {res.page_content} [{res.metadata}]")
            
    except Exception as e:
        print(f"Error: {str(e)}")