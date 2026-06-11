from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserProfileRequest(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Age of the user")
    gender: str = Field(..., description="Gender of the user (Male/Female/Other/All)")
    income: float = Field(..., ge=0, description="Annual family income in INR")
    occupation: str = Field(..., description="Primary occupation (Farmer/Student/Labourer/Entrepreneur/Other/All)")
    education_level: str = Field(..., description="Highest education level (Schooling/Graduate/Post Graduate/None)")
    state: str = Field(..., description="State of residence (e.g. Bihar, Delhi, Maharashtra)")
    social_category: str = Field(..., description="Caste/Social Category (General/OBC/SC/ST)")
    disability_status: bool = Field(default=False, description="Whether the user is differently-abled")

class UserProfileResponse(BaseModel):
    user_id: int
    age: int
    gender: str
    income: float
    occupation: str
    education_level: str
    state: str
    social_category: str
    disability_status: bool

class SchemeDetail(BaseModel):
    scheme_id: str
    scheme_name: str
    category: str
    benefits: str
    description: str
    official_portal: str
    eligibility_criteria: Dict[str, Any]
    required_documents: List[str]
    application_process: List[str]

class SchemeRecommendation(BaseModel):
    scheme_id: str
    scheme_name: str
    category: str
    benefits: str
    description: str
    official_portal: str
    eligibility_score: float
    recommendation_rank: int
    match_reason: str

class SchemeRecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[SchemeRecommendation]

class ChatQueryRequest(BaseModel):
    user_id: int
    query: str
    scheme_id: Optional[str] = None # Optional context: chat about a specific scheme
    model_mode: Optional[str] = "Smart (70B)"

class ChatQueryResponse(BaseModel):
    response: str
    chat_history: List[Dict[str, str]]
