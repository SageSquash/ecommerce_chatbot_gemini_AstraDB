from dotenv import load_dotenv
import os
import httpx
import json

def test_astra_connection():
    load_dotenv()
    
    # Get credentials from environment
    api_endpoint = "https://e1c3e76f-dc81-4b5a-9242-8c0c60a6e9f3-us-east-2.apps.astra.datastax.com"
    token = "AstraCS:fIuSbCtElNrcyAxgzpEddiuE:d3a347ff8bed03ef910fa1911043774b38c8d5e3248c290a7af5f78de58531a3"
    keyspace = os.getenv("ASTRA_DB_KEYSPACE")
    
    # Print configuration (with token partially hidden)
    print("Current Configuration:")
    print(f"API Endpoint: {api_endpoint}")
    print(f"Token: {token[:8]}...{token[-4:] if token else ''}")
    print(f"Keyspace: {keyspace}")
    
    # Verify all required variables are present
    if not all([api_endpoint, token, keyspace]):
        print("\n❌ Error: Missing required environment variables")
        print("Please ensure your .env file contains:")
        print("ASTRA_DB_API_ENDPOINT=your_endpoint")
        print("ASTRA_DB_APPLICATION_TOKEN=your_token")
        print("ASTRA_DB_KEYSPACE=your_keyspace")
        return False
    
    # Test connection
    headers = {
        "X-Cassandra-Token": token,
        "Content-Type": "application/json"
    }
    
    try:
        response = httpx.get(
            f"{api_endpoint}",
            headers=headers,
            timeout=10.0
        )
        response.raise_for_status()
        print("\n✅ Successfully connected to AstraDB!")
        return True
    except httpx.HTTPStatusError as e:
        print(f"\n❌ Connection Error: {e}")
        if e.response.status_code == 401:
            print("\nPossible solutions:")
            print("1. Verify your token is correct and not expired")
            print("2. Make sure you're using the Application Token, not the Database Admin Token")
            print("3. Check if the token has the necessary permissions")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    test_astra_connection()


# from astrapy import DataAPIClient

# # Initialize the client
# client = DataAPIClient("AstraCS:fIuSbCtElNrcyAxgzpEddiuE:d3a347ff8bed03ef910fa1911043774b38c8d5e3248c290a7af5f78de58531a3")
# db = client.get_database_by_api_endpoint(
#   "https://e1c3e76f-dc81-4b5a-9242-8c0c60a6e9f3-us-east-2.apps.astra.datastax.com"
# )

# print(f"Connected to Astra DB: {db.list_collection_names()}")