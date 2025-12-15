"""
Needle Indexing with Auto-Merging Retrieval
Creates small chunks stored in Supabase vector store, with parent pages in local document store
"""

import json
from typing import List, Dict
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.readers.file import PyMuPDFReader
from supabase import create_client, Client

# Handle imports for both module execution and direct script execution
from Config import config

# Configure LlamaIndex settings
Settings.llm = OpenAI(model=config.SUMMARY_MODEL, temperature=config.TEMPERATURE, api_key=config.OPENAI_API_KEY)
Settings.embed_model = OpenAIEmbedding(model=config.EMBEDDING_MODEL, api_key=config.OPENAI_API_KEY)


def load_pdf_with_metadata() -> List[Document]:
    """Load PDF and enrich with metadata from JSON"""
    print("Loading PDF document...")
    
    # Load PDF
    reader = PyMuPDFReader()
    pdf_documents = reader.load(file_path=config.PDF_PATH)
    
    # Load metadata
    with open(config.METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata_dict = json.load(f)
    
    # Enrich documents with metadata
    enriched_docs = []
    for i, doc in enumerate(pdf_documents, start=1):
        page_key = f"page_{i}"
        if page_key in metadata_dict:
            meta = metadata_dict[page_key]
            doc.metadata.update({
                "page_number": meta["page_number"],
                "header": meta["header"],
                "involved_parties": ", ".join(meta["involved_parties"]),
                "date": meta["date"],
                "type": meta["type"],
                "page_id": page_key
            })
            doc.id_ = page_key  # Set document ID for parent reference
            enriched_docs.append(doc)
    
    print(f"[OK] Loaded {len(enriched_docs)} pages with metadata")
    return enriched_docs


def create_needle_chunks(documents: List[Document]) -> tuple:
    """
    Create needle chunks (small, precise chunks) using recursive text splitter:
    - Parent nodes: Full pages (~1200 chars) - stored in document store
    - Child nodes: Small chunks (300 chars with 40 overlap) - stored in vector store
    - Uses paragraph breaks (\n\n) as primary split points
    """
    print("\nCreating needle chunks with paragraph-based splitting...")
    
    # Create parent nodes (full pages)
    parent_nodes = []
    for doc in documents:
        parent_nodes.append(doc)
        print(f"  Parent: {doc.metadata['page_id']} - {doc.metadata['header']}")
    
    child_nodes = []
    for parent_doc in documents:
        # Split by paragraphs first (structured in PDF with \n\n)
        paragraphs = parent_doc.text.split('\n\n')
        
        chunks = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If paragraph is smaller than chunk size, keep it as one chunk
            if len(para) <= config.CHUNK_SIZE:
                from llama_index.core.schema import TextNode
                node = TextNode(text=para)
                node.metadata.update(parent_doc.metadata)
                node.metadata["chunk_index"] = len(chunks)
                node.metadata["parent_id"] = parent_doc.id_
                node.metadata["chunk_id"] = f"{parent_doc.id_}_chunk_{len(chunks)}"
                node.metadata["chunk_size"] = len(para)
                node.id_ = node.metadata["chunk_id"]
                chunks.append(node)
            else:
                # Split paragraph into smaller chunks with overlap
                # Use sentence boundaries as split points
                sentences = para.replace('. ', '.|').split('|')
                
                current_chunk = ""
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    
                    # Check if adding this sentence would exceed chunk size
                    if current_chunk and len(current_chunk) + len(sent) + 1 > config.CHUNK_SIZE:
                        # Finalize current chunk
                        from llama_index.core.schema import TextNode
                        node = TextNode(text=current_chunk.strip())
                        node.metadata.update(parent_doc.metadata)
                        node.metadata["chunk_index"] = len(chunks)
                        node.metadata["parent_id"] = parent_doc.id_
                        node.metadata["chunk_id"] = f"{parent_doc.id_}_chunk_{len(chunks)}"
                        node.metadata["chunk_size"] = len(current_chunk.strip())
                        node.id_ = node.metadata["chunk_id"]
                        chunks.append(node)
                        
                        # Start new chunk with overlap (last ~40 chars from previous chunk)
                        if len(current_chunk) > config.CHUNK_OVERLAP:
                            overlap_text = current_chunk[-config.CHUNK_OVERLAP:]
                            
                            # Ensure overlap starts at a word boundary (not mid-word)
                            first_space = overlap_text.find(' ')
                            if first_space != -1:
                                overlap_text = overlap_text[first_space+1:]
                            
                            # Try to find the start of the last sentence in overlap
                            last_period = overlap_text.rfind('. ')
                            if last_period != -1:
                                overlap_text = overlap_text[last_period+2:]
                            
                            current_chunk = overlap_text + " " + sent
                        else:
                            current_chunk = sent
                    else:
                        current_chunk = current_chunk + (" " if current_chunk else "") + sent
                
                # Add the final chunk from this paragraph
                if current_chunk.strip():
                    from llama_index.core.schema import TextNode
                    node = TextNode(text=current_chunk.strip())
                    node.metadata.update(parent_doc.metadata)
                    node.metadata["chunk_index"] = len(chunks)
                    node.metadata["parent_id"] = parent_doc.id_
                    node.metadata["chunk_id"] = f"{parent_doc.id_}_chunk_{len(chunks)}"
                    node.metadata["chunk_size"] = len(current_chunk.strip())
                    node.id_ = node.metadata["chunk_id"]
                    chunks.append(node)
        
        child_nodes.extend(chunks)
        
        # Show chunk details for verification
        chunk_sizes = [len(c.text) for c in chunks]
        avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunks else 0
        print(f"  -> Created {len(chunks)} child chunks for {parent_doc.metadata['page_id']}")
        print(f"     Chunk sizes: {chunk_sizes} (avg: {avg_size:.0f} chars)")
    
    print(f"\n[OK] Created {len(parent_nodes)} parent nodes and {len(child_nodes)} child chunks")
    return parent_nodes, child_nodes


def store_via_postgres(child_nodes: List[Document], parent_nodes: List[Document], docstore) -> tuple:
    """
    Store chunks using direct PostgreSQL connection (fallback when REST API fails)
    """
    import psycopg2
    import json
    import re
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.core import VectorStoreIndex, StorageContext
    
    print("\n⚠ Using direct PostgreSQL insertion (REST API not ready)...")
    
    # Extract database connection details
    match = re.search(r'https://([^.]+)\.supabase\.co', config.SUPABASE_URL)
    if not match:
        raise Exception("Could not parse Supabase URL")
    
    project_id = match.group(1)
    db_host = f"db.{project_id}.supabase.co"
    
    # Connect to database
    conn = psycopg2.connect(
        host=db_host,
        port=5432,
        database="postgres",
        user="postgres",
        password=config.SUPABASE_DB_PASSWORD
    )
    
    cursor = conn.cursor()
    embed_model = OpenAIEmbedding(model=config.EMBEDDING_MODEL, api_key=config.OPENAI_API_KEY)
    
    print(f"Generating embeddings and storing {len(child_nodes)} chunks via PostgreSQL...")
    
    for i, node in enumerate(child_nodes):
        # Generate embedding
        embedding = embed_model.get_text_embedding(node.text)
        
        # Insert directly into PostgreSQL
        cursor.execute(f"""
            INSERT INTO {config.CHUNKS_TABLE} 
            (chunk_id, content, embedding, metadata, page_number, chunk_index, parent_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (chunk_id) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata,
                page_number = EXCLUDED.page_number,
                chunk_index = EXCLUDED.chunk_index,
                parent_id = EXCLUDED.parent_id;
        """, (
            node.metadata["chunk_id"],
            node.text,
            embedding,
            json.dumps(node.metadata),
            node.metadata["page_number"],
            node.metadata["chunk_index"],
            node.metadata["parent_id"]
        ))
        
        if (i + 1) % 5 == 0 or (i + 1) == len(child_nodes):
            print(f"  Stored {i + 1}/{len(child_nodes)} chunks...")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"[OK] All {len(child_nodes)} chunks stored via PostgreSQL")
    
    # Create index reference
    storage_context = StorageContext.from_defaults(docstore=docstore)
    index = VectorStoreIndex(
        nodes=child_nodes,
        storage_context=storage_context,
        show_progress=False
    )
    
    index.storage_context.persist(persist_dir=config.NEEDLE_INDEX_PATH)
    print(f"[OK] Needle index metadata saved to: {config.NEEDLE_INDEX_PATH}")
    
    return index, docstore


def store_in_supabase(child_nodes: List[Document], parent_nodes: List[Document]) -> tuple:
    """
    Store child chunks in Supabase public tables
    Store parent pages in local document store for auto-merging
    """
    print("\nStoring chunks in Supabase and document store...")
    
    # Initialize Supabase client
    supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    # Initialize local document store for parent nodes
    docstore = SimpleDocumentStore()
    for parent in parent_nodes:
        docstore.add_documents([parent])
    
    # Save document store to disk
    docstore.persist(persist_path=config.DOCSTORE_PATH)
    print(f"[OK] Saved {len(parent_nodes)} parent pages to document store: {config.DOCSTORE_PATH}")
    
    # Generate embeddings and store chunks
    print(f"Generating embeddings for {len(child_nodes)} chunks...")
    from llama_index.embeddings.openai import OpenAIEmbedding
    embed_model = OpenAIEmbedding(model=config.EMBEDDING_MODEL, api_key=config.OPENAI_API_KEY)
    
    for i, node in enumerate(child_nodes):
        # Generate embedding
        embedding = embed_model.get_text_embedding(node.text)
        
        # Prepare data for Supabase
        data = {
            "chunk_id": node.metadata["chunk_id"],
            "content": node.text,
            "embedding": embedding,
            "metadata": node.metadata,
            "page_number": node.metadata["page_number"],
            "chunk_index": node.metadata["chunk_index"],
            "parent_id": node.metadata["parent_id"]
        }
        
        # Upsert into Supabase (insert or update if exists based on chunk_id)
        try:
            result = supabase.table(config.CHUNKS_TABLE).upsert(
                data,
                on_conflict="chunk_id"  # Update if chunk_id already exists
            ).execute()
            
            # Verify insertion was successful
            if not result.data:
                raise Exception(f"Insertion returned empty data - table may not be recognized by REST API")
            
            if (i + 1) % 5 == 0 or (i + 1) == len(child_nodes):
                print(f"  Stored {i + 1}/{len(child_nodes)} chunks...")
        except Exception as e:
            print(f"\n✗ Error storing chunk {i + 1}: {e}")
            print("\nThe Supabase REST API hasn't recognized the table yet.")
            print("Switching to direct PostgreSQL insertion method...")
            
            # Fall back to PostgreSQL direct insertion
            return store_via_postgres(child_nodes, parent_nodes, docstore)
    
    print(f"[OK] All {len(child_nodes)} chunks stored in Supabase table: {config.CHUNKS_TABLE}")
    
    # Create a simple index reference for later use
    from llama_index.core import StorageContext
    storage_context = StorageContext.from_defaults(docstore=docstore)
    
    # Create vector index from child chunks
    index = VectorStoreIndex(
        nodes=child_nodes,
        storage_context=storage_context,
        show_progress=False
    )
    
    # Persist index metadata
    index.storage_context.persist(persist_dir=config.NEEDLE_INDEX_PATH)
    print(f"[OK] Needle index metadata saved to: {config.NEEDLE_INDEX_PATH}")
    
    return index, docstore


def create_needle_index():
    """Main function to create needle index with auto-merge capability"""
    print("=" * 70)
    print("NEEDLE INDEXING - Needle-in-a-Haystack System")
    print("=" * 70)
    
    try:
        # Check if claim_chunks table exists before proceeding
        import psycopg2
        import re
        
        match = re.search(r'https://([^.]+)\.supabase\.co', config.SUPABASE_URL)
        if match:
            project_id = match.group(1)
            db_host = f"db.{project_id}.supabase.co"
            
            try:
                conn = psycopg2.connect(
                    host=db_host,
                    port=5432,
                    database="postgres",
                    user="postgres",
                    password=config.SUPABASE_DB_PASSWORD
                )
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = '{config.CHUNKS_TABLE}'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                
                if not table_exists:
                    print(f"\n✗ ERROR: Table '{config.CHUNKS_TABLE}' does not exist!")
                    print("\nThis table is required for needle indexing.")
                    print("Please run database setup first:")
                    print("  1. From main menu, select option 2 (Create/Recreate Indexing)")
                    print("  2. Or run: python Indexing/create_all_indexes.py")
                    return None, None
                    
            except Exception as e:
                print(f"\n✗ ERROR: Cannot connect to database: {e}")
                print("\nPlease check your database credentials in .env file")
                return None, None
        
        # Validate configuration
        config.validate_config()
        
        # Load documents
        documents = load_pdf_with_metadata()
        
        # Create needle chunks structure
        parent_nodes, child_nodes = create_needle_chunks(documents)
        
        # Store in Supabase and local docstore
        index, docstore = store_in_supabase(child_nodes, parent_nodes)
        
        print("\n" + "=" * 70)
        print("NEEDLE INDEX CREATION COMPLETE!")
        print("=" * 70)
        print(f"\n=== Summary ===")
        print(f"  • Parent pages in docstore: {len(parent_nodes)}")
        print(f"  • Child chunks in Supabase: {len(child_nodes)}")
        print(f"  • Chunk size: {config.CHUNK_SIZE} chars")
        print(f"  • Chunk overlap: {config.CHUNK_OVERLAP} chars")
        print(f"  • Embedding model: {config.EMBEDDING_MODEL}")
        print(f"\n=== Files created ===")
        print(f"  • {config.DOCSTORE_PATH} - Parent page document store")
        print(f"  • {config.NEEDLE_INDEX_PATH}/ - Vector index metadata")
        print(f"\n=== Supabase ===")
        print(f"  • Table: {config.CHUNKS_TABLE}")
        print(f"  • Chunks stored with embeddings")
        print("\n[OK] Ready for auto-merging retrieval!")
        
        return index, docstore
        
    except Exception as e:
        print(f"\n[ERROR] Error creating needle index: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    create_needle_index()


