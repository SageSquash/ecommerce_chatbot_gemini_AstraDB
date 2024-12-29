from dotenv import load_dotenv
import os
import httpx
import json

def test_astra_connection():
    load_dotenv()
    
    # Get credentials from environment
    api_endpoint = ""
    token = ""
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
