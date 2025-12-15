"""
Configuration management for the Insurance Claim Indexing System
Loads environment variables and provides configuration constants
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

# Google AI (Gemini) Configuration for RAGAS Evaluation
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
GEMINI_MODEL = "models/gemini-flash-latest"  # Latest Gemini Flash model

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables. Please check your .env file.")

if not SUPABASE_DB_PASSWORD:
    raise ValueError("SUPABASE_DB_PASSWORD must be set in environment variables. Please check your .env file.")

# Chunking Configuration
CHUNK_SIZE = 300  # Small chunks for precise retrieval
CHUNK_OVERLAP = 40  # Overlap between chunks

# Auto-Merging Configuration
AUTO_MERGE_THRESHOLD = 3  # Number of chunks from same parent needed to trigger merge

# Retrieval Configuration
NEEDLE_TOP_K = 6  # Number of chunks to retrieve for needle queries
SUMMARY_TOP_K = 6  # Total summaries to retrieve (Overview + top ranked detail pages)

# OpenAI Model Configuration
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions
EMBEDDING_DIMENSIONS = 1536
SUMMARY_MODEL = "gpt-4o-mini"  # For generating summaries
TEMPERATURE = 0.1  # Low temperature for consistent summaries

# File Paths
DATA_DIR = "Data"
PDF_PATH = os.path.join(DATA_DIR, "insurance_claim.pdf")  # 10 pages
METADATA_PATH = os.path.join(DATA_DIR, "claim_metadata.json")  # 10 pages
DOCSTORE_PATH = os.path.join("Indexing", "docstore.json")  # Local document store for parent nodes

# Supabase Table Names
CHUNKS_TABLE = "claim_chunks"
SUMMARIES_TABLE = "claim_summaries"

# PostgreSQL Connection String for Supabase
def get_postgres_connection_string():
    """Build PostgreSQL connection string from Supabase credentials"""
    # Extract database host from Supabase URL
    # Example: https://kssdybrlodgkjopindol.supabase.co -> db.kssdybrlodgkjopindol.supabase.co
    host = SUPABASE_URL.replace("https://", "").replace("http://", "")
    db_host = f"db.{host}"
    
    return f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@{db_host}:5432/postgres"

# Index Names (stored in Indexing folder)
NEEDLE_INDEX_PATH = os.path.join("Indexing", "needle_index")  # For needle-in-a-haystack retrieval
SUMMARY_INDEX_PATH = os.path.join("Indexing", "summary_index")

# RAGAS Evaluation Paths
EVALUATION_DIR = "Evaluation"
QUERY_RESULTS_PATH = os.path.join(EVALUATION_DIR, "query_results.json")
EVALUATION_RESULTS_PATH = os.path.join(EVALUATION_DIR, "evaluation_results.json")
EVALUATION_REPORT_PATH = os.path.join(EVALUATION_DIR, "evaluation_report.pdf")

def validate_config():
    """Validate that all required configuration is present"""
    errors = []
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is missing")
    
    if not SUPABASE_URL:
        errors.append("SUPABASE_URL is missing")
        
    if not SUPABASE_KEY:
        errors.append("SUPABASE_KEY is missing")
    
    # Note: GOOGLE_AI_API_KEY is optional (only needed for RAGAS evaluation)
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    print("[OK] Configuration validated successfully")
    return True

if __name__ == "__main__":
    # Test configuration
    print("=" * 60)
    print("Configuration Test")
    print("=" * 60)
    
    try:
        validate_config()
        print(f"\nOpenAI API Key: {OPENAI_API_KEY[:20]}...")
        print(f"Supabase URL: {SUPABASE_URL}")
        print(f"Supabase Key: {SUPABASE_KEY[:20]}...")
        print(f"\nChunk Size: {CHUNK_SIZE}")
        print(f"Chunk Overlap: {CHUNK_OVERLAP}")
        print(f"Embedding Model: {EMBEDDING_MODEL}")
        print(f"Summary Model: {SUMMARY_MODEL}")
        print("\n[OK] All configuration loaded successfully!")
    except Exception as e:
        print(f"\n[ERROR] Configuration error: {e}")
        print("\nPlease make sure you have created a .env file with:")
        print("  - OPENAI_API_KEY")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_KEY")


