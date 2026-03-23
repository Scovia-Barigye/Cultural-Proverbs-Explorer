import streamlit as st
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Sunbird API Configuration
SUNBIRD_API_KEY = os.getenv("SUNBIRD_API_KEY")
SUNFLOWER_API_URL = "https://api.sunbird.ai/tasks/sunflower" # Or appropriate chat endpoint
SUNBIRD_TTS_URL = "https://api.sunbird.ai/tasks/tts"

# Tailwind and styling
def load_css():
    st.markdown(
        """
        <style>
        /* Overall background */
        .stApp {
            background-color: #f5f5f4; /* bg-stone-100 */
        }
        /* Custom serif font for proverbs */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');
        .proverb-text {
            font-family: 'Playfair Display', serif;
        }
        </style>
        <script src="https://cdn.tailwindcss.com"></script>
        """,
        unsafe_allow_html=True
    )

# Load proverbs data
@st.cache_data
def load_proverbs():
    try:
        with open('proverbs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def sunflower_deep_dive(proverb, language):
    if not SUNBIRD_API_KEY:
        return "Please set the SUNBIRD_API_KEY in your .env file."
    
    prompt = f"Explain the cultural significance of this Ugandan proverb: '{proverb}'. How does it reflect the values of the {language} people?"
    
    headers = {
        "Authorization": f"Bearer {SUNBIRD_API_KEY}",
        "Content-Type": "application/json"
    }
    # This payload structure is typical for OpenAI-compatible or similar LLM endpoints
    payload = {
        "model": "sunflower-v1", # Replace with actual Sunbird model name if different
        "messages": [
            {"role": "system", "content": "You are a cultural expert specializing in Ugandan traditions and languages."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        # NOTE: Using /chat/completions as it's a common standard. Adjust to exact Sunbird API URL if needed.
        response = requests.post("https://api.sunbird.ai/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "No interpretation received.")
    except Exception as e:
        return f"Error communicating with Sunbird Sunflower API: {e}"

def generate_tts(text, language):
    if not SUNBIRD_API_KEY:
        return None
    
    headers = {
        "Authorization": f"Bearer {SUNBIRD_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "language": language # E.g., 'lug', 'nyn', etc. 
    }
    try:
        response = requests.post(SUNBIRD_TTS_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.content
    except Exception:
        return None

def main():
    st.set_page_config(page_title="Cultural Proverbs Explorer", page_icon="🌍", layout="wide")
    load_css()
    
    st.title("🌍 Cultural Proverbs Explorer")
    st.markdown("Discover the wisdom of Ugandan proverbs, curated by theme and explained by AI.")
    
    proverbs = load_proverbs()
    
    if not proverbs:
        st.warning("No proverbs found. Please ensure `proverbs.json` exists.")
        return

    # Concept Search
    search_query = st.text_input("💡 Concept Search: Type a life lesson (e.g., 'Patience', 'Hard work')", "")
    
    # Category Filter
    st.markdown("### Filter by Category")
    themes = ["All", "Teamwork", "Patience", "Family", "Leadership"]
    
    # Create horizontal buttons
    cols = st.columns(len(themes))
    selected_theme = "All"
    
    for i, theme in enumerate(themes):
        # We use a state variable to keep track of the selected theme
        if f"theme_filter" not in st.session_state:
            st.session_state.theme_filter = "All"
            
        if cols[i].button(f"[{theme}]", use_container_width=True):
            st.session_state.theme_filter = theme
            
    selected_theme = st.session_state.theme_filter
    st.markdown(f"**Viewing:** {selected_theme}")
    st.divider()

    # Filtering Logic
    filtered_proverbs = proverbs
    if selected_theme != "All":
        filtered_proverbs = [p for p in proverbs if p.get("theme", "") == selected_theme]
        
    if search_query:
        filtered_proverbs = [
            p for p in filtered_proverbs 
            if search_query.lower() in p.get("proverb", "").lower() 
            or search_query.lower() in p.get("explanation", "").lower()
            or search_query.lower() in p.get("translation", "").lower()
            or search_query.lower() in p.get("theme", "").lower()
        ]

    if not filtered_proverbs:
        st.info("No proverbs found matching your criteria.")
        
    # Render Proverbs
    for idx, p in enumerate(filtered_proverbs):
        proverb_text = p.get('proverb', '')
        translation = p.get('translation', '')
        language = p.get('language', 'Unknown')
        theme = p.get('theme', 'Unknown')
        
        # Wrapping each proverb in a styled container
        st.markdown(
            f"""
            <div style="background-color: #fffbeb; padding: 2rem; border-radius: 0.5rem; border: 1px solid #fde68a; margin-bottom: 1rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <span style="background-color: #064e3b; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 500;">
                            {theme}
                        </span>
                        <span style="color: #7f1d1d; margin-left: 0.5rem; font-weight: 600; font-size: 0.875rem;">
                            {language}
                        </span>
                    </div>
                </div>
                <h2 class="proverb-text" style="color: #450a0a; font-size: 1.875rem; margin-top: 1rem; margin-bottom: 0.5rem; line-height: 1.25;">
                    "{proverb_text}"
                </h2>
                <p style="color: #78350f; font-size: 1.125rem; font-style: italic;">
                    {translation}
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Action Buttons specific to each proverb
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🎭 Cultural Deep Dive", key=f"dive_{idx}"):
                with st.spinner("Consulting Sunbird Sunflower..."):
                    interpretation = sunflower_deep_dive(proverb_text, language)
                    st.info(interpretation)
                    
        with col2:
            if st.button("🔊 Listen (Original Language)", key=f"audio_{idx}"):
                with st.spinner("Generating audio..."):
                    # Use language code expected by Sunbird (assuming 'lug' for Luganda)
                    lang_code = "lug" if language.lower() == "luganda" else language.lower()
                    audio_bytes = generate_tts(proverb_text, lang_code)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/wav")
                    else:
                        st.warning("Could not generate audio. Ensure API key is set and endpoint is reachable.")
        st.markdown("<br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
