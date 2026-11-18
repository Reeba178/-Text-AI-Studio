import os
import streamlit as st
from dotenv import load_dotenv
import anthropic
from google import genai

# Load API keys from a local .env file, if one exists.
load_dotenv()

st.set_page_config(
    page_title="Text AI Studio",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Gemini 3.1 Flash-Lite uses this exact API model ID.
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


def call_openai(api_key: str, model: str, prompt: str, temperature: float) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content or "No text was returned."


def call_anthropic(api_key: str, model: str, prompt: str, temperature: float):
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(  # type: ignore[call-arg]
        model=model,
        max_tokens=4096,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return "\n".join(
        block.text
        for block in response.content
        if getattr(block, "type", "") == "text"
    ) or "No text was returned."

def call_gemini(api_key: str, model: str, prompt: str, temperature: float) -> str:
    from google import genai

    client = genai.Client(api_key=api_key)

    # Normalize accidental "models/" prefix, but never alter the actual model ID.
    model = model.strip()
    if model.startswith("models/"):
        model = model.removeprefix("models/")

    if model != "gemini-3.1-flash-lite":
        raise ValueError(
            "Unexpected Gemini model ID. This app is configured for "
            "'gemini-3.1-flash-lite'."
        )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config={"temperature": temperature},
    )

    return response.text or "Gemini returned an empty response."


def run_model(
    provider: str, api_key: str, model: str, prompt: str, temperature: float
) -> str:
    if provider == "OpenAI":
        return call_openai(api_key, model, prompt, temperature)
    if provider == "Anthropic":
        return call_anthropic(api_key, model, prompt, temperature)
    if provider == "Google Gemini":
        return call_gemini(api_key, model, prompt, temperature)
    raise ValueError("Please select a supported AI provider.")


# -------------------- Sidebar --------------------
st.title("✍️ Text AI Studio")
st.caption(
    "Generate, summarize, rewrite, and improve text using your preferred AI provider."
)

with st.sidebar:
    st.header("⚙️ AI Provider")

    provider = st.selectbox("Choose provider", list(PROVIDERS.keys()))
    model = st.selectbox("Choose model", PROVIDERS[provider]["models"])

    env_key = os.getenv(PROVIDERS[provider]["env"], "")
    api_key = st.text_input(
        f"{provider} API key",
        value=env_key,
        type="password",
        help="Your key is used to make API requests. It is not saved by this app.",
    )

    temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower values are more focused; higher values are more creative.",
    )

    st.caption("You can enter your API key here or store it in a private .env file.")

    if provider == "Google Gemini":
        st.caption("Gemini model: gemini-3.1-flash-lite")


# -------------------- Shared request handler --------------------
def submit_prompt(prompt: str):
    if not api_key.strip():
        st.error(f"Please enter your {provider} API key in the sidebar.")
        return

    if not prompt.strip():
        st.warning("Please enter some text or instructions first.")
        return

    try:
        with st.spinner(f"Contacting {provider}..."):
            result = run_model(
                provider=provider,
                api_key=api_key.strip(),
                model=model,
                prompt=prompt,
                temperature=temperature,
            )

        st.session_state["latest_result"] = result
        st.success("Your result is ready.")
        st.markdown(result)

        st.download_button(
            label="⬇️ Download result (.txt)",
            data=result,
            file_name="text_ai_result.txt",
            mime="text/plain",
            use_container_width=True,
        )

    except Exception as exc:
        st.error(f"Request failed: {exc}")
        st.info(
            "Check that your API key is correct, the selected provider has API access "
            "and billing enabled, and the model is available to your account."
        )


# -------------------- Main tabs --------------------
tab_generate, tab_summarize, tab_rewrite = st.tabs(
    ["✨ Text Generation", "📝 Summarization", "🔄 Rewrite & Improve"]
)


# Text generation
with tab_generate:
    st.subheader("Generate new text")

    topic = st.text_area(
        "What should the AI write about?",
        height=130,
        placeholder=(
            "Example: Write a professional LinkedIn post about the benefits "
            "of digital marketing..."
        ),
        key="generation_topic",
    )

    col1, col2 = st.columns(2)

    with col1:
        content_type = st.selectbox(
            "Content type",
            [
                "Blog post",
                "Social media caption",
                "Email",
                "Product description",
                "Essay",
                "Story",
                "Professional bio",
                "Other",
            ],
        )

        tone = st.selectbox(
            "Tone",
            [
                "Professional",
                "Friendly",
                "Creative",
                "Persuasive",
                "Informative",
                "Simple and easy to understand",
            ],
        )

    with col2:
        length = st.selectbox("Length", ["Short", "Medium", "Detailed"])

        language = st.selectbox(
            "Output language",
            ["English", "Urdu", "Roman Urdu", "Arabic", "Other / follow prompt"],
        )

    extra = st.text_input(
        "Extra instructions (optional)",
        placeholder="Include headings, examples, hashtags...",
    )

    if st.button(
        "✨ Generate text", type="primary", use_container_width=True, key="generate_btn"
    ):
        prompt = f"""Create the requested content.

Topic/instructions: {topic}
Content type: {content_type}
Tone: {tone}
Length: {length}
Language: {language}
Additional instructions: {extra}

Make the result clear, useful, original, and well formatted."""
        submit_prompt(prompt)


# Summarization
with tab_summarize:
    st.subheader("Summarize text")

    source_text = st.text_area(
        "Paste the text you want summarized",
        height=260,
        placeholder="Paste an article, notes, report, or other text here...",
        key="summary_source",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        summary_length = st.selectbox(
            "Summary length", ["Very short", "Short", "Detailed"], index=1
        )

    with col2:
        summary_style = st.selectbox(
            "Format",
            ["Bullet points", "Paragraph", "Key takeaways", "Executive summary"],
        )

    with col3:
        summary_language = st.selectbox(
            "Summary language",
            ["Same as source", "English", "Urdu", "Roman Urdu"],
        )

    if st.button(
        "📝 Summarize text",
        type="primary",
        use_container_width=True,
        key="summarize_btn",
    ):
        prompt = f"""Summarize the text below.

Length: {summary_length}
Format: {summary_style}
Language: {summary_language}

Preserve important facts, names, figures, and conclusions.
Do not invent information.

TEXT:
{source_text}"""
        submit_prompt(prompt)


# Rewrite and improve
with tab_rewrite:
    st.subheader("Rewrite and improve text")

    draft = st.text_area(
        "Paste your draft",
        height=230,
        placeholder="Paste the text you want to improve...",
        key="rewrite_source",
    )

    rewrite_goal = st.selectbox(
        "What would you like to improve?",
        [
            "Grammar and spelling",
            "Make it more professional",
            "Make it shorter",
            "Make it clearer and simpler",
            "Make it more engaging",
            "Change tone",
        ],
    )

    desired_tone = st.text_input(
        "Desired tone (optional)",
        placeholder="e.g. warm, confident, formal",
    )

    preserve = st.checkbox(
        "Keep the original meaning and important details", value=True
    )

    if st.button(
        "🔄 Rewrite text",
        type="primary",
        use_container_width=True,
        key="rewrite_btn",
    ):
        prompt = f"""Improve the text below.

Goal: {rewrite_goal}
Desired tone: {desired_tone or 'Choose an appropriate tone'}
Preserve original meaning/details: {preserve}

Return the improved text. Do not add unsupported facts.

TEXT:
{draft}"""
        submit_prompt(prompt)


# -------------------- Footer --------------------
st.divider()
st.caption(
    "Privacy & usage: Your text is sent to the selected AI provider for processing. "
    "Avoid entering confidential information. API usage may incur charges."
)
