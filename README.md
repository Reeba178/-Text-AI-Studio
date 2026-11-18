# Text AI Studio

A beginner-friendly Python app for text generation, summarization, and rewriting.
Choose an API provider: OpenAI, Anthropic, or Google Gemini.

## Features
- Text generation with content type, tone, length, and language options
- Summarization in bullets, paragraphs, key takeaways, or executive-summary format
- Rewrite and improve grammar, clarity, tone, and length
- Download generated output as a `.txt` file
- Password-masked API key input
- Optional local `.env` file for API keys

## 1. Install Python
Use Python 3.10 or newer. During installation on Windows, enable **Add Python to PATH**.

## 2. Open the project folder
Open Command Prompt / Terminal in the folder containing `app.py`.

## 3. Install the libraries
```bash
python -m pip install -r requirements.txt
```

## 4. Add your API key
You can enter the key in the app's sidebar each time, or create a file named `.env` in this folder:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here
```

Only add keys for providers you plan to use. Do not share your `.env` file or upload it publicly.

## 5. Run the app
```bash
python -m streamlit run app.py
```

The app will open in your browser, usually at `http://localhost:8501`.

## API key sources
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Google Gemini: https://aistudio.google.com/app/apikey

## Troubleshooting
- **Invalid API key:** Check that you copied the full key and selected the matching provider.
- **Model unavailable:** Choose another model in the sidebar; model availability depends on your provider account.
- **Quota / billing error:** Check the provider's API billing and usage dashboard. API access may be billed separately from a ChatGPT subscription.
- **Missing library:** Run `python -m pip install -r requirements.txt` again.

## Security notes
- The app does not write the API key entered in the sidebar to disk.
- A local `.env` file is for your own computer; keep it private and add it to `.gitignore` if you use Git.
- Text is sent to the selected provider for processing. Review that provider's privacy and data-retention terms before submitting sensitive content.
