import os
import json
import logging
from google import genai
from backend.database import get_all_schemes

logger = logging.getLogger(__name__)

def check_demographics(profile: dict, criteria: dict) -> bool:
    """
    Stage 1: Rule-based demographic filter.
    Returns True if the user profile satisfies the hard constraints of the scheme.
    """
    # 1. Age check
    user_age = profile.get("age", 0)
    min_age = criteria.get("min_age")
    max_age = criteria.get("max_age")
    if min_age is not None and user_age < min_age:
        return False
    if max_age is not None and user_age > max_age:
        return False
        
    # 2. Income check
    user_income = profile.get("income", 0)
    max_income = criteria.get("max_income")
    if max_income is not None and user_income > max_income:
        return False
        
    # 3. Gender check
    user_gender = profile.get("gender", "All").lower()
    scheme_gender = criteria.get("gender", "All").lower()
    if scheme_gender != "all" and user_gender != "all" and user_gender != scheme_gender:
        return False
        
    # 4. State check
    user_state = profile.get("state", "").strip().lower()
    scheme_states = [s.strip().lower() for s in criteria.get("states", ["All"])]
    if "all" not in scheme_states and user_state not in scheme_states:
        return False
        
    # 5. Caste/Category check
    user_caste = profile.get("social_category", "General").lower()
    scheme_caste = [c.strip().lower() for c in criteria.get("caste", ["All"])]
    if "all" not in scheme_caste and user_caste not in scheme_caste:
        return False
        
    # 6. Occupation check
    user_occ = profile.get("occupation", "Other").lower()
    scheme_occ = [o.strip().lower() for o in criteria.get("occupation", ["All"])]
    if "all" not in scheme_occ and user_occ != "all" and user_occ not in scheme_occ:
        return False
        
    # 7. Disability check
    user_disabled = bool(profile.get("disability_status", False))
    scheme_disabled = bool(criteria.get("disability_required", False))
    if scheme_disabled and not user_disabled:
        return False
        
    return True

def get_heuristic_match(profile: dict, scheme: dict) -> dict:
    """
    Renders a detailed, local heuristic match evaluation.
    This avoids flooding LLM API endpoints with parallel requests during list matching,
    preventing 429 Rate Limit errors and keeping the application sub-second fast.
    """
    score = 85.0  # Base score for matching all hard filters
    reason_parts = []
    
    # 1. State check
    state = profile.get("state")
    scheme_states = scheme["eligibility_criteria"].get("states", ["All"])
    if "all" not in [s.lower() for s in scheme_states]:
        reason_parts.append(f"Scheme is active in your state ({state})")
        score += 3
    
    # 2. Occupation check
    occ = profile.get("occupation")
    scheme_occs = scheme["eligibility_criteria"].get("occupation", ["All"])
    if "all" not in [o.lower() for o in scheme_occs]:
        reason_parts.append(f"Tailored for your occupation ({occ})")
        score += 4
        
    # 3. Income check
    income = profile.get("income", 0)
    max_inc = scheme["eligibility_criteria"].get("max_income")
    if max_inc:
        margin = (max_inc - income) / max_inc
        if margin > 0.5:
            reason_parts.append("Your annual income is well within the low-income threshold")
            score += 4
        else:
            reason_parts.append("Income meets the eligible criteria limit")
            score += 2
            
    # 4. Social Category (Caste) check
    caste = profile.get("social_category")
    scheme_castes = scheme["eligibility_criteria"].get("caste", ["All"])
    if "all" not in [c.lower() for c in scheme_castes]:
        reason_parts.append(f"Eligible under the {caste} social category benefit guidelines")
        score += 3
        
    # 5. Disability check
    disabled = profile.get("disability_status", False)
    scheme_disabled = scheme["eligibility_criteria"].get("disability_required", False)
    if scheme_disabled and disabled:
        reason_parts.append("Specifically covers differently-abled criteria")
        score += 5
        
    if not reason_parts:
        reason_parts.append("Matches all configured demographic eligibility rules")
        
    # Limit score to 100%
    final_score = min(score, 100.0)
    
    reason_str = ". ".join(reason_parts)
    
    return {
        "eligibility_score": final_score,
        "match_reason": f"Eligible: {reason_str}. Key benefits: {scheme['benefits']}"
    }

def evaluate_scheme_eligibility(profile: dict, scheme: dict) -> dict:
    """
    Stage 2: LLM-based nuanced eligibility and scoring.
    Supports both Gemini API and Groq API keys as fallbacks.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    
    if not gemini_key and not groq_key:
        return get_heuristic_match(profile, scheme)
        
    prompt = f"""
You are an expert AI Government Scheme Eligibility Evaluator.
Analyze the user profile and government scheme details below, verify eligibility, and calculate a match score (0-100%).
Also provide a simple, empathetic, and clear explanation of why they qualify and what benefits they will receive.

Important Note: The user has already passed all hard demographic filters (age, gender, income, state, caste, occupation, disability) in our local engine. Therefore, they are eligible. Please calculate a high match score (80% to 100%) indicating how well the scheme's benefits fit the user's specific context, and write an encouraging explanation. Do not give a 0% score.

User Profile:
- Age: {profile['age']}
- Gender: {profile['gender']}
- Annual Income: ₹{profile['income']:,}
- Occupation: {profile['occupation']}
- Education Level: {profile['education_level']}
- State: {profile['state']}
- Caste/Category: {profile['social_category']}
- Differently Abled: {'Yes' if profile['disability_status'] else 'No'}

Scheme Details:
- Name: {scheme['scheme_name']}
- Category: {scheme['category']}
- Description: {scheme['description']}
- Benefits: {scheme['benefits']}
- Eligibility rules configured: {json.dumps(scheme['eligibility_criteria'])}

Your output must be a single JSON object with the keys 'eligibility_score' and 'match_reason' exactly as shown below:
{{
  "eligibility_score": <integer score between 80 and 100>,
  "match_reason": "<A brief, easy-to-understand explanation of why they are eligible, outlining the primary benefits and any documents they should prepare.>"
}}
"""
    # 1. Attempt Gemini Call if key is set
    if gemini_key:
        try:
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            result = json.loads(response.text.strip())
            return {
                "eligibility_score": float(result.get("eligibility_score", 95.0)),
                "match_reason": str(result.get("match_reason", "You are eligible for this scheme."))
            }
        except Exception as e:
            logger.error(f"Gemini API key provided but evaluation call failed: {e}")
            
    # 2. Attempt Groq Call if Gemini fails or is not set
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            result = json.loads(completion.choices[0].message.content.strip())
            return {
                "eligibility_score": float(result.get("eligibility_score", 95.0)),
                "match_reason": str(result.get("match_reason", "You are eligible for this scheme."))
            }
        except Exception as e:
            logger.error(f"Groq API evaluation failed: {e}")
            
    # Heuristic fallback if both APIs fail
    return get_heuristic_match(profile, scheme)

def evaluate_schemes_batch(profile: dict, schemes: list) -> dict:
    """
    Evaluates a list of schemes for a given user profile in a single batch LLM call.
    This avoids Groq/Gemini rate limits by packaging all eligible schemes into a single request,
    while returning personalized, high-quality match reasons for each scheme.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    
    # If no keys are set, fallback to heuristics for all
    if not gemini_key and not groq_key:
        return {s["scheme_id"]: get_heuristic_match(profile, s) for s in schemes}
        
    schemes_input = []
    for s in schemes:
        schemes_input.append({
            "scheme_id": s["scheme_id"],
            "scheme_name": s["scheme_name"],
            "category": s["category"],
            "benefits": s["benefits"],
            "description": s["description"],
            "eligibility_rules": s["eligibility_criteria"]
        })
        
    prompt = f"""
You are an expert AI Government Scheme Eligibility Evaluator.
Analyze the user profile and evaluate eligibility for the list of government schemes provided.
Calculate a match score (0-100%) and write a simple, personalized, and clear match explanation (2-3 sentences) for each scheme explaining why they qualify.

Important Note: The user has already passed all hard demographic filters (age, gender, income, state, caste, occupation, disability) in our local engine for all these schemes. Therefore, they are eligible for all schemes in this list. Please calculate a high match score (80% to 100%) indicating how well the scheme's benefits fit the user's specific context, and write an encouraging, personalized explanation. Do not give a 0% score.

User Profile:
- Age: {profile['age']}
- Gender: {profile['gender']}
- Annual Income: ₹{profile['income']:,}
- Occupation: {profile['occupation']}
- Education Level: {profile['education_level']}
- State: {profile['state']}
- Caste/Category: {profile['social_category']}
- Differently Abled: {'Yes' if profile['disability_status'] else 'No'}

List of Schemes to Evaluate:
{json.dumps(schemes_input, indent=2)}

Your response must be a single JSON object with the key "evaluations" which is a list of objects, each containing:
- "scheme_id": string
- "eligibility_score": integer (between 80 and 100)
- "match_reason": string (a brief, clear, easy-to-understand explanation of why they qualify, personalized using their profile, without redundant emojis)

JSON Format:
{{
  "evaluations": [
    {{
      "scheme_id": "<scheme_id_1>",
      "eligibility_score": 95,
      "match_reason": "As a student residing in Delhi, you qualify for this scheme because..."
    }},
    ...
  ]
}}
"""

    results = {}
    
    # 1. Try Gemini first
    if gemini_key:
        try:
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text.strip())
            for item in data.get("evaluations", []):
                results[item["scheme_id"]] = {
                    "eligibility_score": float(item.get("eligibility_score", 95.0)),
                    "match_reason": str(item.get("match_reason", "You are eligible under the scheme rules."))
                }
        except Exception as e:
            logger.error(f"Gemini batch evaluation failed: {e}")
            
    # 2. Try Groq if Gemini is not set or fails
    if not results and groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(completion.choices[0].message.content.strip())
            for item in data.get("evaluations", []):
                results[item["scheme_id"]] = {
                    "eligibility_score": float(item.get("eligibility_score", 95.0)),
                    "match_reason": str(item.get("match_reason", "You are eligible under the scheme rules."))
                }
        except Exception as e:
            logger.error(f"Groq batch evaluation failed: {e}")
            
    # Fallback to heuristics for any missing evaluations
    for s in schemes:
        sid = s["scheme_id"]
        if sid not in results:
            results[sid] = get_heuristic_match(profile, s)
            
    return results

def match_user_to_schemes(profile: dict) -> list:
    """
    Full pipeline:
    1. Retrieve all schemes.
    2. Filter out schemes that fail hard demographic constraints.
    3. Pre-rank schemes using local fast heuristic scores.
    4. Call Batch LLM evaluation on the top 8 schemes to generate nuanced reasoning.
    5. Merge top-tier LLM evaluations with heuristic-based profiles for the rest.
    6. Sort and rank the final list by score.
    """
    all_schemes = get_all_schemes()
    
    # Step 1 & 2: Hard demographic filter and heuristic pre-scoring
    scored_eligible = []
    for scheme in all_schemes:
        if check_demographics(profile, scheme["eligibility_criteria"]):
            heuristic_res = get_heuristic_match(profile, scheme)
            scored_eligible.append((scheme, heuristic_res))
            
    # Sort by heuristic score descending to find the top candidates
    scored_eligible.sort(key=lambda x: x[1]["eligibility_score"], reverse=True)
    
    # Step 3: Separate top 8 schemes for LLM evaluation and keep the rest as heuristic
    top_n = 8
    top_schemes = [item[0] for item in scored_eligible[:top_n]]
    rest_scored = scored_eligible[top_n:]
    
    # Step 4: Batch LLM evaluation on top candidates
    evaluations = {}
    if top_schemes:
        try:
            evaluations = evaluate_schemes_batch(profile, top_schemes)
        except Exception as e:
            logger.error(f"Error during batch LLM evaluation in match_user_to_schemes: {e}")
            evaluations = {}
            
    recommendations = []
    
    # Process top candidates
    for scheme in top_schemes:
        # Check if we got an LLM response; fallback to heuristic if not
        eval_result = evaluations.get(scheme["scheme_id"])
        if not eval_result:
            eval_result = next(item[1] for item in scored_eligible if item[0]["scheme_id"] == scheme["scheme_id"])
            
        recommendations.append({
            "scheme_id": scheme["scheme_id"],
            "scheme_name": scheme["scheme_name"],
            "category": scheme["category"],
            "benefits": scheme["benefits"],
            "description": scheme["description"],
            "official_portal": scheme["official_portal"],
            "eligibility_score": eval_result["eligibility_score"],
            "match_reason": eval_result["match_reason"]
        })
        
    # Process remaining candidates (heuristics only)
    for scheme, heuristic_res in rest_scored:
        recommendations.append({
            "scheme_id": scheme["scheme_id"],
            "scheme_name": scheme["scheme_name"],
            "category": scheme["category"],
            "benefits": scheme["benefits"],
            "description": scheme["description"],
            "official_portal": scheme["official_portal"],
            "eligibility_score": heuristic_res["eligibility_score"],
            "match_reason": heuristic_res["match_reason"]
        })
        
    # Sort recommendations by eligibility score descending
    recommendations.sort(key=lambda x: x["eligibility_score"], reverse=True)
    
    # Assign correct recommendation ranks after sorting
    for idx, rec in enumerate(recommendations, 1):
        rec["recommendation_rank"] = idx
        
    return recommendations
