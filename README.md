# Scam School - Voice Acting Challenge

A fun party game where players compete to deliver the most convincing scam performance! Record yourself reading scam scripts and get scored on your "scammer skills."

## How to Play

1. Enter your name and select a difficulty level
2. Read the scam script you're given
3. Record yourself performing the script (10 seconds)
4. Get scored on your performance!

## Scoring

- **Content Score (0-100)**: How well you delivered the scam script
- **Voice Score (0-100)**: How convincing you sounded
- **Total Score (0-200)**: Combined score with fun rankings!

### Rankings
| Score | Title |
|-------|-------|
| 0-40 | Honest Citizen |
| 41-80 | Suspicious Caller |
| 81-120 | Amateur Con Artist |
| 121-160 | Professional Grifter |
| 161-200 | Master Scammer |

## Local Development

1. Clone the repo
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key"
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deployment to Streamlit Cloud

1. Fork/clone this repo to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add your `OPENAI_API_KEY` in the Streamlit Cloud secrets settings
5. Deploy!

## Tech Stack

- **Streamlit** - Web UI
- **OpenAI Whisper** - Speech-to-text
- **OpenAI GPT-4o** - Performance scoring
- **Librosa** - Audio analysis
