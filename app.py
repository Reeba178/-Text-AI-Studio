import streamlit as st

st.set_page_config(page_title="Text AI Studio", page_icon="✨")
st.title("✨ Text AI Studio")
st.write("Multi-Provider AI - OpenAI, Anthropic & Gemini")

# --- PROVIDERS ---
PROVIDERS = {
    "OpenAI": {
        "env": "OPENAI_API_KEY",
        "models": ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"],
    },
    "Anthropic": {
        "env": "ANTHROPIC_API_KEY",
        "models": ["claude-3-5-haiku-latest", "claude-3-7-sonnet-latest"],
    },
    "Google Gemini": {
        "env": "GEMINI_API_KEY",
        "models": ["gemini-3.1-flash-lite"],
    },
}

# Sidebar - Choose Provider
st.sidebar.header("⚙️ Settings")
provider_name = st.sidebar.selectbox("Choose Provider:", list(PROVIDERS.keys()))
model_name = st.sidebar.selectbox("Choose Model:", PROVIDERS[provider_name]["models"])

st.sidebar.info(f"Using: **{provider_name}**\nModel: `{model_name}`")

text = st.text_area("Enter text:", height=150, placeholder="Type or paste your text here...")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Classify", "Sentiment", "Summarize", "Rewrite", "Grammar Fix", "Translate"])

def ask(prompt):
    if not text.strip():
        st.warning("Please enter some text first!")
        return
    with st.spinner(f"AI is thinking with {provider_name}..."):
        try:
            api_key = st.secrets[PROVIDERS[provider_name]["env"]]
            result = ""
            if provider_name == "OpenAI":
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                res = client.chat.completions.create(model=model_name, messages=[{"role": "user", "content": prompt}])
                result = res.choices[0].message.content
            elif provider_name == "Anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                res = client.messages.create(model=model_name, max_tokens=1000, messages=[{"role": "user", "content": prompt}])
                result = res.content[0].text
            else:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)
                result = model.generate_content(prompt).text
            st.success(result)
        except Exception as e:
            st.error(f"Error: {e}")
            st.info(f"Check if {PROVIDERS[provider_name]['env']} is added in Streamlit Secrets!")

with tab1:
    if st.button("🔍 Classify Text"):
        ask(f"Classify this text into a category like Business, Sports, Technology, Health, Education, etc. and give reason: {text}")
with tab2:
    if st.button("💬 Analyze Sentiment"):
        ask(f"Analyze sentiment. Give Sentiment: Positive/Negative/Neutral, Confidence Score, and Reason: {text}")
with tab3:
    if st.button("📝 Summarize"):
        ask(f"Summarize this text in 2-3 short lines, simple English: {text}")
with tab4:
    style = st.selectbox("Rewrite style:", ["Formal", "Simple", "Funny", "Professional"])
    if st.button("✍️ Rewrite"):
        ask(f"Rewrite this text in {style} style, keep same meaning: {text}")
with tab5:
    if st.button("✅ Fix Grammar"):
        ask(f"Fix grammar and spelling of this text, show corrected version only: {text}")
with tab6:
    lang = st.selectbox("Translate to:", ["Urdu", "English", "Hindi", "French", "Arabic"])
    if st.button("🌍 Translate"):
        ask(f"Translate this text to {lang}: {text}")
