import os
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from google import genai

from backend.models import (
    UserProfileRequest, UserProfileResponse,
    SchemeRecommendation, SchemeRecommendationResponse,
    ChatQueryRequest, ChatQueryResponse,
    SchemeDetail
)
from backend.database import (
    save_user_profile, get_user_profile,
    get_all_schemes, get_scheme_by_id,
    save_recommendations, get_user_recommendations,
    save_query_history, get_chat_history, init_db
)
from backend.eligibility import match_user_to_schemes
from backend.vector_store import query_vector_store

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Scheme-AI Backend", version="1.0.0")

# CORS middleware for communication with frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on start
@app.on_event("startup")
def startup_event():
    logger.info("Starting up FastAPI application...")
    init_db()

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(profile: UserProfileRequest):
    try:
        user_id = save_user_profile(
            age=profile.age,
            gender=profile.gender,
            income=profile.income,
            occupation=profile.occupation,
            education_level=profile.education_level,
            state=profile.state,
            social_category=profile.social_category,
            disability_status=profile.disability_status
        )
        return UserProfileResponse(user_id=user_id, **profile.dict())
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Failed to save user profile.")

@app.get("/api/profile/{user_id}", response_model=UserProfileResponse)
def read_profile(user_id: int):
    profile = get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    # Map database 1/0 to boolean
    profile["disability_status"] = bool(profile["disability_status"])
    return UserProfileResponse(**profile)

@app.post("/api/recommendations", response_model=SchemeRecommendationResponse)
def get_recommendations(profile_req: UserProfileResponse):
    try:
        profile = profile_req.dict()
        # Evaluate eligibility using our hybrid engine
        recommendations_list = match_user_to_schemes(profile)
        
        # Save recommendations to SQLite
        save_recs_db = [
            (rec["scheme_id"], rec["eligibility_score"], rec["recommendation_rank"])
            for rec in recommendations_list
        ]
        save_recommendations(profile_req.user_id, save_recs_db)
        
        # Format response
        recs = [SchemeRecommendation(**rec) for rec in recommendations_list]
        return SchemeRecommendationResponse(user_id=profile_req.user_id, recommendations=recs)
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@app.get("/api/schemes", response_model=List[SchemeDetail])
def list_schemes():
    return get_all_schemes()

@app.get("/api/schemes/{scheme_id}", response_model=SchemeDetail)
def get_scheme(scheme_id: str):
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@app.post("/api/chat", response_model=ChatQueryResponse)
def chat_with_assistant(chat_req: ChatQueryRequest):
    user_id = chat_req.user_id
    query = chat_req.query
    scheme_id = chat_req.scheme_id
    
    # 1. Retrieve context from ChromaDB
    results = query_vector_store(query, scheme_id=scheme_id, n_results=3)
    
    if results:
        context = "\n\n".join([doc["content"] for doc in results])
    else:
        # Fallback to DB query if Chroma search returns nothing
        context = "No specific official guidelines found."
        if scheme_id:
            scheme = get_scheme_by_id(scheme_id)
            if scheme:
                context = f"Scheme Name: {scheme['scheme_name']}\nDescription: {scheme['description']}\nBenefits: {scheme['benefits']}"
                
    # 2. Get user profile context to personalize the chat
    profile = get_user_profile(user_id) if user_id else None
    profile_str = ""
    if profile:
        profile_str = (
            f"User Profile context:\n"
            f"- Age: {profile['age']}\n"
            f"- Gender: {profile['gender']}\n"
            f"- Occupation: {profile['occupation']}\n"
            f"- State: {profile['state']}\n"
            f"- Category: {profile['social_category']}\n"
            f"- Income: ₹{profile['income']:,}\n"
            f"- Differently Abled: {'Yes' if profile['disability_status'] else 'No'}\n"
        )
        
    # 3. Retrieve user's eligible schemes to inject into LLM context
    recs_str = "None"
    if user_id:
        try:
            recs = get_user_recommendations(user_id)
            if recs:
                recs_str = ", ".join([f"{r['scheme_name']} (Match: {int(r['eligibility_score'])}%)" for r in recs])
        except Exception as recs_err:
            logger.error(f"Error fetching user recommendations for chat context: {recs_err}")

    # 4. Retrieve recent conversation history
    history = get_chat_history(user_id, limit=6) if user_id else []
    history_str = ""
    for h in history:
        history_str += f"User: {h['user_query']}\nAssistant: {h['assistant_response']}\n"
        
    # 5. Draft conversational prompt
    prompt = f"""
You are "Scheme-AI Helper", an empathetic, highly expert government welfare scheme assistant for Indian citizens.
Your goal is to answer the user's questions about government schemes clearly, simply, and accurately, using ONLY the provided official Context below.

{profile_str}

User's Active Recommended Schemes (User is eligible for these according to the database recommendations):
- {recs_str}

Retrieved Official Context:
\"\"\"
{context}
\"\"\"

Recent Chat History:
{history_str}

User Question: {query}

Instructions:
1. Ground your answers strictly in the Retrieved Context. Do not make up facts or URL links.
2. Translate complex administrative jargon into plain, clear language.
3. Be encouraging and empathetic. If the user profile is provided, personalize details (e.g. "As a student from Delhi...").
4. Provide structured, bullet-point instructions for "how to apply" and "required documents" when relevant.
5. If the context does not contain enough information to answer, politely state: "I don't have that information in my official scheme guidelines, but you can check the official portal."

Response:
"""

    gemini_key = os.environ.get("GEMINI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    
    response_text = ""
    
    # 1. Try Gemini
    if gemini_key:
        try:
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            response_text = response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API key provided but chat request failed: {e}")
            
    # 2. Try Groq (Llama-3) if Gemini fails or is not provided
    if not response_text and groq_key:
        from groq import Groq
        client = Groq(api_key=groq_key)
        
        preferred_model = "llama-3.3-70b-versatile" if chat_req.model_mode == "Smart (70B)" else "llama-3.1-8b-instant"
        fallback_model = "llama-3.1-8b-instant"
        
        try:
            completion = client.chat.completions.create(
                model=preferred_model,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = completion.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Groq primary model call ({preferred_model}) failed: {e}. Attempting auto-fallback to 8b.")
            if preferred_model != fallback_model:
                try:
                    completion = client.chat.completions.create(
                        model=fallback_model,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    response_text = completion.choices[0].message.content.strip()
                    # Prepend a small fallback notice
                    response_text = "⚠️ *(Auto-fallback to Fast Mode due to high API traffic)*\n\n" + response_text
                except Exception as fallback_err:
                    logger.error(f"Groq API chat fallback failed: {fallback_err}")
            else:
                logger.error(f"Groq API call failed and no alternative fallback possible.")
            
    # 3. Fallback to Local/Demo mode response if both keys fail or are missing
    if not response_text:
        logger.warning("No working API keys found. Returning search-grounded local response.")
        response_text = (
            "I'm running in demo mode without an LLM API key. Here is the relevant information "
            "retrieved from our official database:\n\n"
        )
        for i, res in enumerate(results, 1):
            response_text += f"**Section {i}**:\n{res['content']}\n\n"
        
    # Save to SQLite chat history
    if user_id:
        save_query_history(user_id, query, response_text)
        
    chat_hist = get_chat_history(user_id) if user_id else []
    return ChatQueryResponse(
        response=response_text,
        chat_history=[{"user": h["user_query"], "assistant": h["assistant_response"]} for h in chat_hist]
    )
