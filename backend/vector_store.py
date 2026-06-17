import os
import json
import math
import random
import logging
import sqlite3
from google import genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if running on Vercel
IS_VERCEL = os.environ.get("VERCEL") == "1"

ORIGINAL_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "scheme_ai.db")

if IS_VERCEL:
    DB_PATH = "/tmp/scheme_ai.db"
    # Copy from original read-only location to /tmp on startup if it doesn't exist
    if not os.path.exists(DB_PATH) and os.path.exists(ORIGINAL_DB_PATH):
        import shutil
        shutil.copyfile(ORIGINAL_DB_PATH, DB_PATH)
else:
    DB_PATH = ORIGINAL_DB_PATH

# Log environment key state
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    logger.warning("GEMINI_API_KEY environment variable not found. RAG will use smart keyword search fallback.")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_vector_store_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Vector_Store (
        chunk_id TEXT PRIMARY KEY,
        scheme_id TEXT,
        content TEXT NOT NULL,
        metadata TEXT NOT NULL, -- JSON string
        embedding TEXT NOT NULL  -- JSON string list of floats
    )
    """)
    conn.commit()
    conn.close()

def get_embedding(text: str) -> list:
    """
    Generate embedding for text.
    If GEMINI_API_KEY is not set, returns a mock random embedding of size 768.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return [random.uniform(-0.1, 0.1) for _ in range(768)]
        
    try:
        # Create client using the new SDK
        client = genai.Client(api_key=api_key)
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        logger.error(f"Error calling Gemini Embedding API: {e}. Falling back to mock embedding.")
        return [random.uniform(-0.1, 0.1) for _ in range(768)]

def add_documents_to_store(docs: list, metadatas: list, ids: list):
    """
    docs: list of strings (chunks of text)
    metadatas: list of dicts (e.g. {"scheme_id": "pm_kisan"})
    ids: list of strings (unique chunk ids)
    """
    init_vector_store_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for doc, meta, cid in zip(docs, metadatas, ids):
        logger.info(f"Generating embedding for chunk {cid}...")
        emb = get_embedding(doc)
        scheme_id = meta.get("scheme_id")
        
        cursor.execute("""
        INSERT OR REPLACE INTO Vector_Store (chunk_id, scheme_id, content, metadata, embedding)
        VALUES (?, ?, ?, ?, ?)
        """, (cid, scheme_id, doc, json.dumps(meta), json.dumps(emb)))
        
    conn.commit()
    conn.close()
    logger.info(f"Successfully added/updated {len(docs)} documents in custom SQLite vector store.")

def dot_product(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))

def magnitude(v):
    return math.sqrt(sum(a * a for a in v))

def cosine_similarity(v1, v2):
    mag1 = magnitude(v1)
    mag2 = magnitude(v2)
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product(v1, v2) / (mag1 * mag2)

def query_vector_store(query_text: str, scheme_id: str = None, n_results: int = 3):
    """
    query_text: search query
    scheme_id: optional filter to search within a specific scheme
    """
    init_vector_store_db()
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    # CASE 1: Gemini API Key is available -> Use standard Cosine Similarity Vector Search
    if gemini_key:
        logger.info(f"Querying vector store using Gemini Vector Search: '{query_text}'")
        query_emb = get_embedding(query_text)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if scheme_id:
            rows = cursor.execute("SELECT * FROM Vector_Store WHERE scheme_id = ?", (scheme_id,)).fetchall()
        else:
            rows = cursor.execute("SELECT * FROM Vector_Store").fetchall()
            
        conn.close()
        
        scored_results = []
        for row in rows:
            row_dict = dict(row)
            emb = json.loads(row_dict["embedding"])
            sim = cosine_similarity(query_emb, emb)
            distance = 1.0 - sim
            
            scored_results.append({
                "content": row_dict["content"],
                "metadata": json.loads(row_dict["metadata"]),
                "distance": distance,
                "similarity": sim
            })
            
        scored_results.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_results[:n_results]
        
    # CASE 2: No Gemini API Key -> Use smart keyword overlap search (highly accurate fallback)
    else:
        logger.info(f"Querying vector store using Keyword Fallback: '{query_text}'")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if scheme_id:
            rows = cursor.execute("SELECT * FROM Vector_Store WHERE scheme_id = ?", (scheme_id,)).fetchall()
        else:
            rows = cursor.execute("SELECT * FROM Vector_Store").fetchall()
            
        conn.close()
        
        scored_results = []
        query_words = set(query_text.lower().replace("?", "").replace(",", "").split())
        
        for row in rows:
            row_dict = dict(row)
            content = row_dict["content"].lower()
            
            # Basic word match score
            word_matches = sum(1.0 for w in query_words if w in content)
            
            # Boost score significantly if key terms from the scheme ID match
            scheme_id_words = row_dict["scheme_id"].replace("_", " ").lower().split()
            boost = sum(3.0 for w in scheme_id_words if w in query_text.lower())
            
            score = word_matches + boost
            
            scored_results.append({
                "content": row_dict["content"],
                "metadata": json.loads(row_dict["metadata"]),
                "distance": 1.0 / (score + 0.01),
                "similarity": score
            })
            
        # Sort by match score descending
        scored_results.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_results[:n_results]
