import os
import json
import logging
from backend.database import init_db, upsert_scheme, get_db_connection
from backend.vector_store import add_documents_to_store

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_data():
    logger.info("Initializing SQLite database...")
    init_db()
    
    schemes_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "schemes.json")
    if not os.path.exists(schemes_json_path):
        logger.error(f"Seeding file not found at {schemes_json_path}")
        return
        
    with open(schemes_json_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)
        
    logger.info("Clearing existing schemes and vector indexes for clean seed...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Recommendation")
    cursor.execute("DELETE FROM Scheme_Details")
    cursor.execute("DELETE FROM Vector_Store")
    conn.commit()
    conn.close()
    
    logger.info(f"Loaded {len(schemes)} schemes from json.")
    
    docs = []
    metadatas = []
    ids = []
    
    for scheme in schemes:
        scheme_id = scheme["id"]
        # Save to SQLite
        logger.info(f"Upserting scheme {scheme_id} to SQLite database...")
        upsert_scheme(
            scheme_id=scheme_id,
            scheme_name=scheme["name"],
            category=scheme["category"],
            benefits=scheme["benefits"],
            description=scheme["description"],
            eligibility_criteria=scheme["eligibility_rules"],
            required_documents=scheme["required_documents"],
            application_process=scheme["application_steps"],
            official_portal=scheme["official_portal"]
        )
        
        # Prepare text chunks for RAG in ChromaDB
        # Chunk 1: Overview & Benefits
        overview_text = f"Scheme Name: {scheme['name']}\nCategory: {scheme['category']}\nDescription: {scheme['description']}\nBenefits: {scheme['benefits']}"
        docs.append(overview_text)
        metadatas.append({"scheme_id": scheme_id, "type": "overview"})
        ids.append(f"{scheme_id}_overview")
        
        # Chunk 2: Eligibility Rules
        rules_str = ", ".join([f"{k}: {v}" for k, v in scheme['eligibility_rules'].items()])
        eligibility_text = f"Scheme Name: {scheme['name']}\nDetailed Eligibility Rules:\n{rules_str}"
        docs.append(eligibility_text)
        metadatas.append({"scheme_id": scheme_id, "type": "eligibility"})
        ids.append(f"{scheme_id}_eligibility")
        
        # Chunk 3: Application Process
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(scheme['application_steps'])])
        app_text = f"Scheme Name: {scheme['name']}\nHow to Apply (Step-by-Step):\n{steps_text}\nOfficial Portal Link: {scheme['official_portal']}"
        docs.append(app_text)
        metadatas.append({"scheme_id": scheme_id, "type": "application"})
        ids.append(f"{scheme_id}_application")
        
        # Chunk 4: Documents Required
        docs_text = ", ".join(scheme['required_documents'])
        documents_text = f"Scheme Name: {scheme['name']}\nRequired Documents for Application:\n{docs_text}"
        docs.append(documents_text)
        metadatas.append({"scheme_id": scheme_id, "type": "documents"})
        ids.append(f"{scheme_id}_documents")
        
    logger.info("Adding documents to ChromaDB Vector Store...")
    add_documents_to_store(docs, metadatas, ids)
    logger.info("Ingestion completed successfully!")

if __name__ == "__main__":
    ingest_data()
