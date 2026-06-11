import os
import sys

# Ensure parent directory is in sys.path to resolve backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_scheme_by_id, get_all_schemes
from backend.vector_store import query_vector_store
from backend.eligibility import match_user_to_schemes

def test_retrieval():
    print("--- Testing Database Retrieval ---")
    new_ids = ["pm_surya_ghar", "pm_vishwakarma", "lakhpati_didi", "pmbjp", "igndps", "ignwps"]
    for sid in new_ids:
        scheme = get_scheme_by_id(sid)
        if scheme:
            print(f"✅ Retrieved '{scheme['scheme_name']}' under category '{scheme['category']}'")
        else:
            print(f"❌ Failed to retrieve scheme ID: {sid}")

def test_vector_search():
    print("\n--- Testing Vector/Keyword Search ---")
    queries = [
        "solar panels rooftop subsidy",
        "carpenter artisan loan pm vishwakarma",
        "drone training for women self help group",
        "disability pension BPL",
        "cheap generic medicines Jan Aushadhi"
    ]
    for q in queries:
        print(f"Query: '{q}'")
        results = query_vector_store(q, n_results=1)
        if results:
            best_match = results[0]
            print(f"  👉 Match: {best_match['metadata']['scheme_id']} ({best_match['metadata']['type']})")
            print(f"  👉 Similarity/Score: {best_match['similarity']:.2f}")
        else:
            print("  ❌ No match found.")

def test_eligibility():
    print("\n--- Testing Demographic Eligibility Matching ---")
    
    # 1. Profile: Low-income woman entrepreneur in self-help group
    profile_female_entrepreneur = {
        "age": 32,
        "gender": "Female",
        "income": 45000,
        "occupation": "Entrepreneur",
        "education_level": "Schooling",
        "state": "Bihar",
        "social_category": "OBC",
        "disability_status": False
    }
    
    recs = match_user_to_schemes(profile_female_entrepreneur)
    print("Eligible schemes for 32-year old low-income female entrepreneur:")
    found_lakhpati = False
    for r in recs[:5]:
        print(f"  ⭐ {r['scheme_name']} (Score: {r['eligibility_score']}%)")
        if r['scheme_id'] == "lakhpati_didi":
            found_lakhpati = True
            
    if found_lakhpati:
        print("✅ Lakhpati Didi correctly recommended!")
    else:
        print("❌ Lakhpati Didi NOT recommended.")

    # 2. Profile: Severely disabled low-income citizen
    profile_disabled = {
        "age": 28,
        "gender": "Male",
        "income": 20000,
        "occupation": "Other",
        "education_level": "None",
        "state": "Uttar Pradesh",
        "social_category": "SC",
        "disability_status": True
    }
    
    recs_disabled = match_user_to_schemes(profile_disabled)
    print("\nEligible schemes for 28-year old disabled citizen:")
    found_igndps = False
    for r in recs_disabled[:5]:
        print(f"  ⭐ {r['scheme_name']} (Score: {r['eligibility_score']}%)")
        if r['scheme_id'] == "igndps":
            found_igndps = True
            
    if found_igndps:
        print("✅ IGNDPS disability pension correctly recommended!")
    else:
        print("❌ IGNDPS disability pension NOT recommended.")

if __name__ == "__main__":
    test_retrieval()
    test_vector_search()
    test_eligibility()
