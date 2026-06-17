import streamlit as st
import requests
import json
import os
import sys
import plotly.express as px
import pandas as pd
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
# Add parent directory to sys.path so we can import backend if needed for fallback
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Try to import backend modules directly for local fallback
try:
    from backend.database import save_user_profile, get_user_profile, get_all_schemes, get_chat_history, save_query_history, get_user_recommendations
    from backend.eligibility import match_user_to_schemes
    from backend.vector_store import query_vector_store
    from google import genai
    BACKEND_AVAILABLE = True
except Exception as e:
    BACKEND_AVAILABLE = False
    print(f"Direct backend imports failed: {e}")

# Page config
st.set_page_config(
    page_title="Scheme-AI: Government Scheme Eligibility Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Server Configuration
API_BASE_URL = "https://scheme-ai-chi.vercel.app/api"

def check_api_server():
    """Verify if the FastAPI backend is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=1.0)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Custom CSS for rich premium styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

/* Main layout overrides */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
h1, h2, h3, .title-text {
    font-family: 'Outfit', sans-serif;
}

/* Remove Streamlit default top padding */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
}

/* Main title styling */
.main-title {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 800;
    margin-top: 0rem !important;
    margin-bottom: 0.2rem;
}
.sub-title {
    color: #475569;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

/* Premium Card Design */
.scheme-card {
    background-color: #ffffff;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.scheme-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    border-top-color: #3b82f6;
    border-right-color: #3b82f6;
    border-bottom-color: #3b82f6;
}

/* Category Specific Left Borders */
.scheme-card-education { border-left: 6px solid #2563eb; }     /* blue */
.scheme-card-health { border-left: 6px solid #10b981; }        /* green */
.scheme-card-agriculture { border-left: 6px solid #f97316; }   /* orange */
.scheme-card-housing { border-left: 6px solid #06b6d4; }       /* cyan */
.scheme-card-employment { border-left: 6px solid #64748b; }    /* slate */
.scheme-card-labour { border-left: 6px solid #f59e0b; }        /* amber */
.scheme-card-women { border-left: 6px solid #ec4899; }         /* pink */
.scheme-card-senior { border-left: 6px solid #6366f1; }        /* indigo */
.scheme-card-digital { border-left: 6px solid #8b5cf6; }       /* violet */
.scheme-card-financial { border-left: 6px solid #ef4444; }     /* red */
.scheme-card-default { border-left: 6px solid #cbd5e1; }       /* neutral gray */

.scheme-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.scheme-title {
    font-size: 1.55rem;
    font-weight: 800;
    color: #0f172a !important;
    margin: 0;
}

/* Why you qualify box */
.reason-box {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 14px 18px;
    border-radius: 10px;
    margin: 14px 0 16px 0;
    font-size: 0.9rem;
    color: #334155;
    line-height: 1.5;
}

/* Official Portal Link */
.portal-link {
    color: #2563eb !important;
    font-size: 0.85rem;
    font-weight: 600;
    text-decoration: none !important;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: all 0.2s ease;
    border-bottom: 1.5px solid transparent;
    padding-bottom: 1px;
}
.portal-link:hover {
    color: #1d4ed8 !important;
    border-bottom-color: #1d4ed8;
}

/* Custom Badges */
.badge {
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
}
.badge-agriculture { background-color: #ecfdf5; color: #047857; }
.badge-health { background-color: #f0f9ff; color: #0369a1; }
.badge-education { background-color: #faf5ff; color: #7e22ce; }
.badge-business { background-color: #fff7ed; color: #c2410c; }
.badge-financial { background-color: #fef2f2; color: #b91c1c; }
.badge-social { background-color: #f8fafc; color: #475569; }
.badge-housing { background-color: #e0f2fe; color: #0369a1; }
.badge-employment { background-color: #f1f5f9; color: #334155; }
.badge-labour { background-color: #fef3c7; color: #92400e; }
.badge-women { background-color: #fce7f3; color: #be185d; }
.badge-senior { background-color: #e0e7ff; color: #4338ca; }
.badge-digital { background-color: #fae8ff; color: #86198f; }

.match-container {
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    padding: 6px 12px;
    border-radius: 8px;
}
.match-label {
    font-size: 0.75rem;
    color: #166534;
    font-weight: 600;
}
.match-val {
    font-size: 1rem;
    font-weight: 800;
    color: #15803d;
}

.benefit-box {
    background-color: #f8fafc;
    border-left: 4px solid #3b82f6;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 14px 0;
    font-size: 0.9rem;
    color: #334155;
}

/* Metric stats styling */
.stat-box {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #334155;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}
.stat-val {
    font-size: 2.2rem;
    font-weight: 800;
    color: #38bdf8;
    margin-bottom: 4px;
}
.stat-lbl {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94a3b8;
}

/* Chat bubble styling */
.chat-bubble {
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    font-size: 0.95rem;
    line-height: 1.5;
    max-width: 85%;
}
.chat-user {
    background-color: #eff6ff;
    color: #1e3a8a;
    border: 1px solid #bfdbfe;
    margin-left: auto;
    border-bottom-right-radius: 2px;
}
.chat-assistant {
    background-color: #f8fafc;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    margin-right: auto;
    border-bottom-left-radius: 2px;
}

/* Sleek Mic Button Styling */
#mic-button-container {
    pointer-events: auto !important;
    position: relative !important;
    z-index: 999999 !important;
}

#custom-mic-btn {
    pointer-events: auto !important;
    position: relative !important;
    z-index: 999999 !important;
    cursor: pointer !important;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #ffffff;
    display: flex;
    justify-content: center;
    align-items: center;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    outline: none;
    padding: 0;
    margin: 0 auto;
}

#custom-mic-btn:hover {
    background-color: #0f172a;
    border-color: #475569;
    transform: scale(1.05);
}

#custom-mic-btn.active {
    background-color: #ef4444;
    border-color: #f87171;
    animation: mic-pulse 1.5s infinite;
}

#custom-mic-btn:disabled {
    background-color: #475569;
    cursor: not-allowed;
    opacity: 0.6;
}

@keyframes mic-pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
    100% {
        box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
        transform: scale(1);
    }
}
</style>
""", unsafe_allow_html=True)

# Check backend status
is_api_running = check_api_server()

# App state initialization
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "selected_scheme_id" not in st.session_state:
    st.session_state.selected_scheme_id = None
if "selected_scheme_name" not in st.session_state:
    st.session_state.selected_scheme_name = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None
if "locked_profile" not in st.session_state:
    st.session_state.locked_profile = {
        "age": 25,
        "gender": "Male",
        "income": 150000,
        "occupation": "Student",
        "education_level": "None",
        "state": "Central (All India)",
        "social_category": "General",
        "disability_status": False
    }
    # Initial startup save to backend
    initial_p = st.session_state.locked_profile
    if is_api_running:
        try:
            res = requests.post(f"{API_BASE_URL}/profile", json=initial_p)
            if res.status_code == 201:
                st.session_state.user_id = res.json()["user_id"]
        except Exception as e:
            print(f"Error saving initial profile: {e}")
    elif BACKEND_AVAILABLE:
        st.session_state.user_id = save_user_profile(**initial_p)

# Sidebar: User Profile Inputs inside form to isolate reruns
with st.sidebar.form("profile_form"):
    st.markdown("### Citizen Profiling")
    st.markdown("Provide your demographics to check eligible schemes.")
    
    default_p = st.session_state.locked_profile
    
    age = st.slider("Age (Years)", 0, 100, int(default_p["age"]))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(default_p["gender"]))
    income = st.number_input("Annual Family Income (INR)", min_value=0, value=int(default_p["income"]), step=10000)
    occupation = st.selectbox("Occupation", ["Student", "Farmer", "Labourer", "Entrepreneur", "Other"], index=["Student", "Farmer", "Labourer", "Entrepreneur", "Other"].index(default_p["occupation"]))
    education_level = st.selectbox("Education Level", ["None", "Schooling", "Graduate", "Post Graduate"], index=["None", "Schooling", "Graduate", "Post Graduate"].index(default_p["education_level"]))
    
    states_list = [
        "Central (All India)", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
        "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
        "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir", "Puducherry"
    ]
    state = st.selectbox("State / Union Territory", states_list, index=states_list.index(default_p["state"]))
    social_category = st.selectbox("Social Category", ["General", "OBC", "SC", "ST"], index=["General", "OBC", "SC", "ST"].index(default_p["social_category"]))
    disability_status = st.checkbox("Differently Abled (Disability status)", value=default_p["disability_status"])
    
    submit_btn = st.form_submit_button("Find My Schemes & Lock Profile")

if submit_btn:
    st.session_state.locked_profile = {
        "age": age,
        "gender": gender,
        "income": income,
        "occupation": occupation,
        "education_level": education_level,
        "state": state,
        "social_category": social_category,
        "disability_status": disability_status
    }
    # Start fresh chat session and clear cached recommendations
    st.session_state.chat_history = []
    st.session_state.selected_scheme_id = None
    st.session_state.selected_scheme_name = None
    st.session_state.recommendations = None
    
    # Save the updated profile to backend
    profile_data = st.session_state.locked_profile
    if is_api_running:
        try:
            res = requests.post(f"{API_BASE_URL}/profile", json=profile_data)
            if res.status_code == 201:
                st.session_state.user_id = res.json()["user_id"]
        except Exception as e:
            st.error(f"Error saving profile: {e}")
    elif BACKEND_AVAILABLE:
        st.session_state.user_id = save_user_profile(**profile_data)
        
    st.success("Profile committed! Recommendation list and chat refreshed.")
    st.rerun()


# Display server connection status below the form
if not is_api_running:
    if BACKEND_AVAILABLE:
        st.sidebar.info("Mode: In-Process Engine (FastAPI not detected)")
    else:
        st.sidebar.error("Critical Error: Backend modules not found.")
else:
    st.sidebar.success("Mode: FastAPI Server Connected")
# Main Dashboard Layout
st.markdown('<h1 class="main-title">Scheme-AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Your Conversational Government Scheme Eligibility & Application Assistant</p>', unsafe_allow_html=True)

# Tabs
tab_recs, tab_chat, tab_explore = st.tabs([
    "Eligible Recommendations",
    "Conversational Application Guide",
    "Browse All Schemes"
])

# Retrieve Recommendations
if st.session_state.recommendations is None and st.session_state.user_id:
    with st.spinner("Scheme-AI is running eligibility checks using AI..."):
        if is_api_running:
            try:
                profile_response = st.session_state.locked_profile.copy()
                profile_response["user_id"] = st.session_state.user_id
                res = requests.post(f"{API_BASE_URL}/recommendations", json=profile_response)
                if res.status_code == 200:
                    st.session_state.recommendations = res.json()["recommendations"]
            except Exception as e:
                st.error(f"Error fetching recommendations: {e}")
        elif BACKEND_AVAILABLE:
            st.session_state.recommendations = match_user_to_schemes(st.session_state.locked_profile)

recommendations = st.session_state.recommendations or []

# Tab 1: Recommendations Dashboard
with tab_recs:
    if not recommendations:
        st.info("No schemes match your demographic profile. Try adjusting your sidebar selections (e.g. state, income, or age).")
    else:
        # Dashboard Overview Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-val">{len(get_all_schemes()) if BACKEND_AVAILABLE else 10}</div>
                <div class="stat-lbl">Total Schemes Checked</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-val">{len(recommendations)}</div>
                <div class="stat-lbl">Eligible Schemes Found</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            avg_match = sum(r.get("eligibility_score", r.get("eligibility_score", 90)) for r in recommendations) / len(recommendations)
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-val">{avg_match:.1f}%</div>
                <div class="stat-lbl">Avg Match Confidence</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            sectors_covered = len(set(r["category"] for r in recommendations))
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-val">{sectors_covered}</div>
                <div class="stat-lbl">Sectors Covered</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Grid layout for schemes and visualizations
        col_list, col_viz = st.columns([2, 1])
        
        with col_list:
            st.markdown("### Recommended Schemes")
            for rec in recommendations:
                category_class = f"badge-{rec['category'].split('&')[0].strip().lower()}"
                cat_key = rec['category'].split('&')[0].strip().lower()
                valid_cats = {"education", "health", "agriculture", "housing", "employment", "labour", "women", "senior", "digital", "financial"}
                card_border_class = f"scheme-card-{cat_key}" if cat_key in valid_cats else "scheme-card-default"
                
                # HTML template for scheme card
                st.markdown(f"""
                <div class="scheme-card {card_border_class}">
                    <div class="scheme-header">
                        <span class="badge {category_class}">{rec['category']}</span>
                        <div class="match-container">
                            <span class="match-label">Match Score</span>
                            <span class="match-val">{int(rec['eligibility_score'])}%</span>
                        </div>
                    </div>
                    <h3 class="scheme-title">{rec['scheme_name']}</h3>
                    <div style="margin-top: 8px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                        <span style="color:#475569; font-size:0.85rem; font-weight: 600;">Official Portal:</span>
                        <a class="portal-link" href="{rec['official_portal']}" target="_blank">Visit Official Website ↗</a>
                    </div>
                    <p style="color:#334155; font-size:0.95rem; margin: 12px 0;">{rec['description']}</p>
                    <div class="benefit-box">
                        <strong>Key Benefits:</strong> {rec['benefits']}
                    </div>
                    <div class="reason-box">
                        <strong>Match Reason:</strong> {rec['match_reason']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Dynamic action button for each scheme
                btn_col1, btn_col2 = st.columns([1, 4])
                with btn_col1:
                    if st.button("Guide Me", key=f"btn_{rec['scheme_id']}"):
                        st.session_state.selected_scheme_id = rec['scheme_id']
                        st.session_state.selected_scheme_name = rec['scheme_name']
                        st.rerun()
                
                # Render success message outside columns to span full width of the card
                if st.session_state.selected_scheme_id == rec['scheme_id']:
                    st.success(f"Context set to: **{rec['scheme_name']}**. Please open the 'Conversational Application Guide' tab above!")
        
        with col_viz:
            st.markdown("### Analytics Insights")
            
            # 1. Category Distribution of Eligible Schemes
            df_recs = pd.DataFrame(recommendations)
            cat_counts = df_recs["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig_pie = px.pie(
                cat_counts, names="Category", values="Count",
                title="Eligibility Distribution by Category",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=280)
            st.plotly_chart(fig_pie, use_container_width=True)
            


# Tab 2: Conversational Application Guide (RAG Chatbot)
with tab_chat:
    st.markdown("### Conversational Application Assistant")

    # Layout toggles side by side
    col_toggles1, col_toggles2 = st.columns(2)
    with col_toggles1:
        model_mode = st.radio(
            "Assistant Reasoning Level:",
            ["Smart (70B)", "Fast (8B)"],
            index=0,
            horizontal=True,
            help="Smart uses Meta Llama-3.3 70B for deep policy analysis. Fast uses Meta Llama-3.1 8B to minimize latency."
        )
    with col_toggles2:
        voice_lang = st.radio(
            "Voice Dictation Language:",
            ["English (IN)", "Hindi (IN)"],
            index=0,
            horizontal=True,
            help="Select the language for voice dictation transcription."
        )
    
    lang_code = "en-IN" if voice_lang == "English (IN)" else "hi-IN"
    
    # Active scheme context display
    if st.session_state.selected_scheme_id:
        st.info(f"Current Focus: **{st.session_state.selected_scheme_name}**  \nTo clear focus and ask general queries, click the button below.")
        if st.button("Clear Scheme Focus"):
            st.session_state.selected_scheme_id = None
            st.session_state.selected_scheme_name = None
            st.rerun()
    else:
        st.markdown("*Ask questions like: 'Am I eligible for PM-KISAN?', 'What documents do I need for housing subsidy?'*")

    # Render Chat History
    chat_container = st.container()
    
    # Initialize chat history display
    if is_api_running and st.session_state.user_id:
        try:
            # Fetch history from DB via API
            # Just use local session state list to avoid roundtrips, but we can query it on first load.
            pass
        except Exception as e:
            print(f"Error fetching API chat history: {e}")
            
    with chat_container:
        for chat in st.session_state.chat_history:
            st.markdown(f'<div class="chat-bubble chat-user"><strong>You:</strong><br>{chat["user"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-bubble chat-assistant"><strong>Scheme-AI:</strong><br>{chat["assistant"]}</div>', unsafe_allow_html=True)

    # Chat Input Form
    with st.form("chat_form", clear_on_submit=True):
        col_text, col_mic, col_send = st.columns([10, 1.2, 1.8])
        with col_text:
            user_query = st.text_input("Type your message here...", placeholder="Ask how to apply, which documents are required, etc.", label_visibility="collapsed")
        with col_mic:
            st.markdown('<div id="mic-button-container" style="display: flex; justify-content: center; align-items: center; height: 100%; margin-top: 4px;"></div>', unsafe_allow_html=True)
        with col_send:
            submitted = st.form_submit_button("Send 🚀", use_container_width=True)
        if submitted and user_query:
            st.session_state.chat_history.append({"user": user_query.strip(), "assistant": "Thinking..."})
            st.rerun()
    iframe_code = f"""
    <script>
    (function() {{
        const parentWin = window.parent;
        const doc = parentWin.document;
        
        // Remove existing script tag if any
        const SCRIPT_ID = 'speech-recognition-bridge-script';
        const existingScript = doc.getElementById(SCRIPT_ID);
        if (existingScript) {{
            existingScript.remove();
        }}
        
        // Inject script to execute in the parent's window context
        const script = doc.createElement('script');
        script.id = SCRIPT_ID;
        script.innerHTML = `
            (function() {{
                function logToBackend(msg) {{
                    fetch('https://scheme-ai-chi.vercel.app/api/log', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ message: msg }})
                    }}).catch(err => {{}});
                }}
                
                const console = {{
                    log: (msg) => logToBackend("[INFO] " + msg),
                    error: (msg) => logToBackend("[ERROR] " + msg),
                    warn: (msg) => logToBackend("[WARN] " + msg)
                }};
                
                console.log("MediaRecorder script loaded in parent context.");
                
                if (window.__speech_mic_timer) {{
                    clearTimeout(window.__speech_mic_timer);
                }}
                
                function initParentMic() {{
                    const container = document.getElementById('mic-button-container');
                    const inputEl = Array.from(document.querySelectorAll('input[type="text"], textarea'))
                        .find(el => el.placeholder && el.placeholder.includes("Ask how to apply"));
                        
                    if (!container || !inputEl) {{
                        console.log("Searching for container or inputEl...");
                        window.__speech_mic_timer = setTimeout(initParentMic, 200);
                        return;
                    }}
                    
                    console.log("Container and Input elements found. Setting up mic button...");
                    
                    // Clear container to avoid duplicate elements/listeners
                    container.innerHTML = '';
                    container.style.display = 'flex';
                    container.style.flexDirection = 'column';
                    container.style.alignItems = 'center';
                    container.style.justifyContent = 'center';
                    container.style.cursor = 'pointer';
                    container.style.pointerEvents = 'auto';
                    
                    const btn = document.createElement('div');
                    btn.id = 'custom-mic-btn';
                    btn.title = "Click to dictate prompt";
                    btn.style.pointerEvents = 'none'; // Click bubbles up to container
                    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" x2="12" y1="19" y2="22"></line></svg>';
                    container.appendChild(btn);
                    
                    const statusText = document.createElement('div');
                    statusText.id = 'mic-status-text';
                    statusText.style.fontSize = '10px';
                    statusText.style.color = '#64748b';
                    statusText.style.marginTop = '4px';
                    statusText.style.textAlign = 'center';
                    statusText.style.whiteSpace = 'nowrap';
                    statusText.style.pointerEvents = 'none'; // Click bubbles up to container
                    statusText.innerText = 'Click to speak';
                    container.appendChild(statusText);
                    
                    let mediaRecorder = null;
                    let audioChunks = [];
                    let isRecording = false;
                    let initialText = "";
                    let streamRef = null;
                    
                    function stopRecording() {{
                        console.log("Stopping recording...");
                        isRecording = false;
                        btn.classList.remove('active');
                        btn.title = "Click to dictate prompt";
                        
                        if (mediaRecorder && mediaRecorder.state !== 'inactive') {{
                            mediaRecorder.stop();
                        }}
                        if (streamRef) {{
                            streamRef.getTracks().forEach(track => track.stop());
                        }}
                    }}
                    
                    function startRecording() {{
                        audioChunks = [];
                        console.log("Requesting mic access...");
                        
                        navigator.mediaDevices.getUserMedia({{ audio: true }})
                            .then(stream => {{
                                console.log("Mic access granted. Setting up MediaRecorder...");
                                streamRef = stream;
                                mediaRecorder = new MediaRecorder(stream, {{ mimeType: 'audio/webm' }});
                                
                                mediaRecorder.ondataavailable = event => {{
                                    if (event.data.size > 0) {{
                                        audioChunks.push(event.data);
                                    }}
                                }};
                                
                                mediaRecorder.onstop = () => {{
                                    console.log("MediaRecorder stopped. Preparing upload...");
                                    statusText.innerText = 'Transcribing...';
                                    statusText.style.color = '#e28743'; // Orange
                                    
                                    const audioBlob = new Blob(audioChunks, {{ type: 'audio/webm' }});
                                    const formData = new FormData();
                                    formData.append('file', audioBlob, 'audio.webm');
                                    const lang = "{lang_code}".split('-')[0];
                                    formData.append('language', lang);
                                    
                                    console.log("Uploading audio.webm (" + audioBlob.size + " bytes) in lang=" + lang + " to /api/transcribe...");
                                    
                                    fetch('https://scheme-ai-chi.vercel.app/api/transcribe', {{
                                        method: 'POST',
                                        body: formData
                                    }})
                                    .then(res => {{
                                        if (!res.ok) {{
                                            throw new Error('Server returned ' + res.status);
                                        }}
                                        return res.json();
                                    }})
                                    .then(data => {{
                                        console.log("Transcription response: " + data.transcript);
                                        if (data.transcript && data.transcript.trim()) {{
                                            let newValue = initialText;
                                            if (newValue && !newValue.endsWith(' ')) {{
                                                newValue += ' ';
                                            }}
                                            newValue += data.transcript.trim();
                                            
                                            const prototype = inputEl.tagName === 'TEXTAREA' 
                                                ? HTMLTextAreaElement.prototype 
                                                : HTMLInputElement.prototype;
                                            const nativeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
                                            nativeValueSetter.call(inputEl, newValue);
                                            
                                            const ev = new Event('input', {{ bubbles: true }});
                                            inputEl.dispatchEvent(ev);
                                        }}
                                        statusText.innerText = 'Click to speak';
                                        statusText.style.color = '#64748b';
                                    }})
                                    .catch(err => {{
                                        console.error("Transcription failed: " + err.message);
                                        statusText.innerText = 'Error: ' + err.message;
                                        statusText.style.color = '#ef4444';
                                        btn.classList.remove('active');
                                    }});
                                }};
                                
                                mediaRecorder.start();
                                isRecording = true;
                                btn.classList.add('active');
                                statusText.innerText = 'Recording...';
                                statusText.style.color = '#ef4444';
                                initialText = inputEl.value;
                                
                                // Auto stop recording after 20 seconds to prevent massive uploads
                                setTimeout(() => {{
                                    if (isRecording) {{
                                        console.log("Auto-stopping recording after 20 seconds limit.");
                                        stopRecording();
                                    }}
                                }}, 20000);
                            }})
                            .catch(err => {{
                                console.error("Mic access denied or error: " + err.name + " - " + err.message);
                                statusText.innerText = 'Error: ' + err.name;
                                statusText.style.color = '#ef4444';
                                btn.classList.remove('active');
                            }});
                    }}
                    
                    container.onclick = (e) => {{
                        e.preventDefault();
                        e.stopPropagation();
                        console.log("Mic container clicked! isRecording = " + isRecording);
                        if (isRecording) {{
                            stopRecording();
                        }} else {{
                            startRecording();
                        }}
                    }};
                }}
                
                initParentMic();
            }})();
        `;
        doc.body.appendChild(script);
    }})();
    </script>
    """
    st.components.v1.html(iframe_code, height=0)

    # Process response if last message is from user and assistant is "Thinking..."
    if st.session_state.chat_history and st.session_state.chat_history[-1]["assistant"] == "Thinking...":
        query = st.session_state.chat_history[-1]["user"]
        assistant_resp = ""
        
        if is_api_running:
            try:
                res = requests.post(f"{API_BASE_URL}/chat", json={
                    "user_id": st.session_state.user_id,
                    "query": query,
                    "scheme_id": st.session_state.selected_scheme_id,
                    "model_mode": model_mode
                })
                if res.status_code == 200:
                    assistant_resp = res.json()["response"]
            except Exception as e:
                assistant_resp = f"API Error: Failed to contact assistant service. {e}"
        elif BACKEND_AVAILABLE:
            # In-process RAG calling
            # 1. Retrieve RAG chunks
            results = query_vector_store(query, scheme_id=st.session_state.selected_scheme_id)
            context = "\n\n".join([doc["content"] for doc in results]) if results else "No specific official guidelines found."
            
            # 2. Get user profile
            profile = get_user_profile(st.session_state.user_id) if st.session_state.user_id else None
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
            if st.session_state.user_id:
                try:
                    recs = get_user_recommendations(st.session_state.user_id)
                    if recs:
                        recs_str = ", ".join([f"{r['scheme_name']} (Match: {int(r['eligibility_score'])}%)" for r in recs])
                except Exception as recs_err:
                    print(f"Error fetching user recommendations for chat: {recs_err}")

            # 4. Retrieve history
            history = get_chat_history(st.session_state.user_id, limit=6) if st.session_state.user_id else []
            history_str = ""
            for h in history:
                history_str += f"User: {h['user_query']}\nAssistant: {h['assistant_response']}\n"
                
            # 5. Draft conversational prompt
            prompt = f"""
You are "Scheme-AI Helper", an empathetic, highly expert government welfare scheme assistant for Indian citizens.
Answer the user's questions about government schemes based ONLY on the provided Context below.

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
1. Ground your answers strictly in the Retrieved Context. Do not make up facts.
2. Translate complex administrative jargon into plain, clear language.
3. Be encouraging and empathetic. If user profile details are relevant, personalize the details.
4. Provide structured instructions for required documents and how to apply.
5. If the context does not contain enough info, state that you don't have it but provide general guidance.

Response:
"""
            gemini_key = os.environ.get("GEMINI_API_KEY")
            groq_key = os.environ.get("GROQ_API_KEY")
            
            # 1. Try Gemini
            if gemini_key:
                try:
                    client = genai.Client(api_key=gemini_key)
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=prompt
                    )
                    assistant_resp = response.text.strip()
                except Exception as e:
                    logger.error(f"Gemini direct call failed: {e}")
                    
            # 2. Try Groq (Llama-3)
            if not assistant_resp and groq_key:
                from groq import Groq
                client = Groq(api_key=groq_key)
                
                preferred_model = "llama-3.3-70b-versatile" if model_mode == "Smart (70B)" else "llama-3.1-8b-instant"
                fallback_model = "llama-3.1-8b-instant"
                
                try:
                    completion = client.chat.completions.create(
                        model=preferred_model,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    assistant_resp = completion.choices[0].message.content.strip()
                except Exception as e:
                    logger.warning(f"Groq direct call ({preferred_model}) failed: {e}. Attempting auto-fallback to 8b.")
                    if preferred_model != fallback_model:
                        try:
                            completion = client.chat.completions.create(
                                model=fallback_model,
                                messages=[{"role": "user", "content": prompt}]
                            )
                            assistant_resp = completion.choices[0].message.content.strip()
                            assistant_resp = "⚠️ *(Auto-fallback to Fast Mode due to high API traffic)*\n\n" + assistant_resp
                        except Exception as fallback_err:
                            logger.error(f"Groq direct fallback call failed: {fallback_err}")
                    else:
                        logger.error(f"Groq direct call failed and no alternative fallback possible.")
                    
            # 3. Fallback to Demo Mode
            if not assistant_resp:
                assistant_resp = (
                    "**Demo Mode (No API Key)**: Here is the information retrieved from our knowledge base:\n\n"
                )
                for i, r in enumerate(results, 1):
                    assistant_resp += f"**Section {i} ({r['metadata'].get('type', 'detail')})**:\n{r['content']}\n\n"
                    
            # Save query to database history
            if st.session_state.user_id:
                save_query_history(st.session_state.user_id, query, assistant_resp)
        else:
            assistant_resp = "Error: Backend engine not available."
            
        # Update session state with response
        st.session_state.chat_history[-1]["assistant"] = assistant_resp
        st.rerun()

# Tab 3: Browse All Schemes
with tab_explore:
    st.markdown("### Complete Schemes Repository")
    st.markdown("Search and browse the guidelines, criteria, and details of all seeded schemes.")
    
    # Retrieve all schemes
    all_schemes = []
    if is_api_running:
        try:
            res = requests.get(f"{API_BASE_URL}/schemes")
            if res.status_code == 200:
                all_schemes = res.json()
        except Exception as e:
            st.error(f"Error listing schemes: {e}")
    elif BACKEND_AVAILABLE:
        all_schemes = get_all_schemes()
        
    if all_schemes:
        search_query = st.text_input("Search schemes by name, category, or keyword:", placeholder="e.g. Kisan, Scholarship, Loan")
        
        filtered_schemes = []
        for s in all_schemes:
            if (search_query.lower() in s["scheme_name"].lower() or 
                search_query.lower() in s["category"].lower() or 
                search_query.lower() in s["description"].lower()):
                filtered_schemes.append(s)
                
        for scheme in filtered_schemes:
            with st.expander(f"{scheme['scheme_name']} ({scheme['category']})"):
                st.markdown(f"**Description:** {scheme['description']}")
                st.markdown(f"**Benefits:** {scheme['benefits']}")
                
                # Eligibility criteria breakdown
                st.markdown("**Eligibility Parameters:**")
                rules = scheme["eligibility_criteria"]
                rules_col1, rules_col2 = st.columns(2)
                with rules_col1:
                    st.markdown(f"- **Min Age:** {rules.get('min_age') or 'N/A'} years")
                    st.markdown(f"- **Max Age:** {rules.get('max_age') or 'N/A'} years")
                    income_limit = f"₹{rules.get('max_income'):,}" if rules.get('max_income') else "No limit"
                    st.markdown(f"- **Max Annual Family Income:** {income_limit}")
                    st.markdown(f"- **Gender:** {rules.get('gender') or 'All'}")
                with rules_col2:
                    st.markdown(f"- **Eligible Occupations:** {', '.join(rules.get('occupation', []))}")
                    st.markdown(f"- **Eligible Categories:** {', '.join(rules.get('caste', []))}")
                    st.markdown(f"- **States:** {', '.join(rules.get('states', []))}")
                    st.markdown(f"- **Disability Required:** {'Yes' if rules.get('disability_required') else 'No'}")
                
                # Documents & Application steps
                st.markdown("---")
                doc_col, step_col = st.columns(2)
                with doc_col:
                    st.markdown("**Required Documents:**")
                    for doc in scheme["required_documents"]:
                        st.markdown(f"- {doc}")
                with step_col:
                    st.markdown("**Application Steps:**")
                    for i, step in enumerate(scheme["application_process"], 1):
                        st.markdown(f"{i}. {step}")
                        
                st.markdown(f"**Official Website Link:** [{scheme['official_portal']}]({scheme['official_portal']})")
    else:
        st.info("No schemes seeded in the database. Run the ingestion script to populate schemes.")
