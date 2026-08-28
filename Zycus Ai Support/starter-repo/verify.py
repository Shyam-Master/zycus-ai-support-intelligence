from app.utils.data_loader import DataLoader
from app.rag.ingest import ingest_documents
from app.rag.retriever import retrieve_documents

def main():
    print("1. Loading datasets...")
    accounts = DataLoader.load_accounts()
    tickets = DataLoader.load_tickets()
    print(f"   Accounts loaded: {len(accounts)}")
    print(f"   Tickets loaded: {len(tickets)}")
    
    print("\n2. Retrieving known account...")
    try:
        acc = DataLoader.get_account('ACC-3336')
        print(f"   Found account: {acc['company']} ({acc['account_id']})")
    except Exception as e:
        print(f"   Error: {e}")
        
    print("\n3. Retrieving last 90 days tickets for account ACC-3336...")
    recent_tickets = DataLoader.get_tickets_last_90_days('ACC-3336')
    print(f"   Found {len(recent_tickets)} recent tickets.")
    
    print("\n4. Building KB Index...")
    num_chunks, num_files = ingest_documents()
    print(f"   Indexed {num_files} markdown files into {num_chunks} chunks.")
    
    queries = [
        ("Authentication / SSO", "SSO configuration not working for new users."),
        ("Billing or plans", "What are the differences between Starter and Business plans?"),
        ("Product/integration issue", "Webhook from CloudSync not reaching Snowflake")
    ]
    
    print("\n5. Running Retrieval Queries...")
    for category, query in queries:
        print(f"\n--- Query: {category} --- '{query}'")
        results = retrieve_documents(query, top_k=2)
        if not results:
            print("   No results found below distance threshold.")
        for idx, res in enumerate(results):
            print(f"   Result {idx+1}: {res['document']} (Dist: {res['distance']:.3f})")
            print(f"   Snippet: {res['chunk_text'][:100]}...")

if __name__ == '__main__':
    main()
