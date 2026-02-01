"""
Scam School - Voice Acting Challenge Game
A fun party game where you try to sound like a convincing scammer!
"""

import os
import streamlit as st

from analysis import process_audio_for_game, GameScore
from prompts import get_random_prompt, ScamPrompt
from leaderboard import Leaderboard, format_leaderboard_table


def get_api_key():
    """Get OpenAI API key from Streamlit secrets or environment."""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        return st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass
    
    # Fall back to environment variable (for local development)
    return os.environ.get("OPENAI_API_KEY")

# Page config
st.set_page_config(
    page_title="Scam School",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #FF4B4B;
        font-size: 3em;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-top: 0;
    }
    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .big-score {
        font-size: 4em;
        font-weight: bold;
        margin: 0;
    }
    .title-badge {
        background: gold;
        color: black;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin: 10px 0;
    }
    .prompt-box {
        background: #1a1a2e;
        color: #eee;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        font-family: monospace;
        font-size: 1.1em;
        line-height: 1.6;
    }
    .tip-box {
        background: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "game_state" not in st.session_state:
        st.session_state.game_state = "welcome"  # welcome, playing, results
    if "player_name" not in st.session_state:
        st.session_state.player_name = ""
    if "current_prompt" not in st.session_state:
        st.session_state.current_prompt = None
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "medium"
    if "last_score" not in st.session_state:
        st.session_state.last_score = None
    if "leaderboard" not in st.session_state:
        st.session_state.leaderboard = Leaderboard()


def show_welcome_screen():
    """Display the welcome/start screen."""
    st.markdown('<h1 class="main-title">🎭 Scam School</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">The Voice Acting Challenge</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    ### How to Play
    
    1. **Enter your name** and select a difficulty
    2. **Read the scam script** you're given
    3. **Record yourself** performing the script (10 seconds)
    4. **Get scored** on your scammer performance!
    
    *Can you sound like a convincing con artist?* 🎬
    """)
    
    st.markdown("---")
    
    # Player name input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        name = st.text_input(
            "Enter your name",
            value=st.session_state.player_name,
            placeholder="Your scammer alias..."
        )
        st.session_state.player_name = name
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            index=1
        )
        st.session_state.difficulty = difficulty.lower()
    
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎬 Start Game", use_container_width=True, type="primary"):
            if st.session_state.player_name.strip():
                # Get a random prompt
                st.session_state.current_prompt = get_random_prompt(st.session_state.difficulty)
                st.session_state.game_state = "playing"
                st.rerun()
            else:
                st.error("Please enter your name!")
    
    # Show leaderboard
    st.markdown("---")
    st.markdown("### 🏆 Leaderboard")
    
    top_scores = st.session_state.leaderboard.get_top_scores(5)
    if top_scores:
        for i, entry in enumerate(top_scores, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            st.markdown(f"{medal} **{entry.player_name}** - {entry.total_score}/200 ({entry.title})")
    else:
        st.info("No scores yet! Be the first to play!")


def show_playing_screen():
    """Display the game playing screen with prompt and recording."""
    prompt: ScamPrompt = st.session_state.current_prompt
    
    st.markdown(f'<h1 class="main-title">🎭 Your Mission</h1>', unsafe_allow_html=True)
    
    # Show prompt info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Category", prompt.category)
    with col2:
        st.metric("Difficulty", prompt.difficulty.title())
    with col3:
        st.metric("Title", prompt.title)
    
    st.markdown("---")
    
    # The scam script
    st.markdown("### 📜 Read this script:")
    st.markdown(f'<div class="prompt-box">{prompt.script}</div>', unsafe_allow_html=True)
    
    # Acting tips
    st.markdown(f'<div class="tip-box">💡 <strong>Acting Tip:</strong> {prompt.tips}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recording section
    st.markdown("### 🎙️ Record Your Performance")
    st.info("Click the microphone to record a 10-second clip of you reading the script above!")
    
    # Audio recorder
    try:
        from audio_recorder_streamlit import audio_recorder
        
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#FF4B4B",
            neutral_color="#6c757d",
            icon_size="2x",
            pause_threshold=10.0,  # 10 second recording
        )
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎯 Submit for Scoring", use_container_width=True, type="primary"):
                    with st.spinner("🔍 Analyzing your performance..."):
                        api_key = get_api_key()
                        if not api_key:
                            st.error("OpenAI API key not found! Set it in Streamlit secrets or environment.")
                        else:
                            try:
                                score = process_audio_for_game(
                                    audio_bytes=audio_bytes,
                                    original_prompt=prompt.script,
                                    difficulty=prompt.difficulty,
                                    api_key=api_key
                                )
                                st.session_state.last_score = score
                                
                                # Add to leaderboard
                                st.session_state.leaderboard.add_entry(
                                    player_name=st.session_state.player_name,
                                    total_score=score.total_score,
                                    content_score=score.content_score,
                                    voice_score=score.voice_score,
                                    title=score.title,
                                    difficulty=prompt.difficulty,
                                    category=prompt.category
                                )
                                
                                st.session_state.game_state = "results"
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error analyzing audio: {str(e)}")
            
            with col2:
                if st.button("🔄 Re-record", use_container_width=True):
                    st.rerun()
    
    except ImportError:
        st.error("""
        Audio recorder not available. Please install it:
        ```
        pip install audio-recorder-streamlit
        ```
        """)
    
    # Back button
    st.markdown("---")
    if st.button("← Back to Menu"):
        st.session_state.game_state = "welcome"
        st.rerun()


def show_results_screen():
    """Display the results/score screen."""
    score: GameScore = st.session_state.last_score
    prompt: ScamPrompt = st.session_state.current_prompt
    
    st.markdown('<h1 class="main-title">🎉 Results!</h1>', unsafe_allow_html=True)
    
    # Big score display
    st.markdown(f"""
    <div class="score-box">
        <p class="big-score">{score.total_score}</p>
        <p style="font-size: 1.5em; margin: 0;">out of 200</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Title badge
    st.markdown(f"""
    <div style="text-align: center;">
        <span class="title-badge">🏅 {score.title}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Score breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Content Score")
        st.progress(score.content_score / 100)
        st.markdown(f"**{score.content_score}/100**")
        st.markdown(f"*{score.content_feedback}*")
    
    with col2:
        st.markdown("### 🎤 Voice Score")
        st.progress(score.voice_score / 100)
        st.markdown(f"**{score.voice_score}/100**")
        st.markdown(f"*{score.voice_feedback}*")
    
    st.markdown("---")
    
    # What you said
    with st.expander("📜 What you said (transcript)"):
        st.markdown(f"> {score.transcript}")
    
    # Voice analysis details
    with st.expander("🔬 Voice Analysis Details"):
        chars = score.characteristics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Pitch", f"{chars.average_pitch:.1f} Hz")
            st.metric("Pitch Variance", f"{chars.pitch_variance:.1f}")
            st.metric("Speaking Rate", f"{chars.speaking_rate:.1f}")
        with col2:
            st.metric("Voice Energy", f"{chars.energy_mean:.4f}")
            st.metric("Tempo", f"{chars.tempo:.1f} BPM")
            st.metric("Duration", f"{chars.duration:.1f}s")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎬 Play Again", use_container_width=True, type="primary"):
            st.session_state.current_prompt = get_random_prompt(st.session_state.difficulty)
            st.session_state.game_state = "playing"
            st.rerun()
    
    with col2:
        if st.button("🔄 New Difficulty", use_container_width=True):
            st.session_state.game_state = "welcome"
            st.rerun()
    
    with col3:
        if st.button("🏆 Leaderboard", use_container_width=True):
            st.session_state.game_state = "welcome"
            st.rerun()
    
    # Player ranking
    rank = st.session_state.leaderboard.get_player_rank(st.session_state.player_name)
    if rank:
        st.success(f"🏆 You're ranked #{rank} on the leaderboard!")


def main():
    """Main app entry point."""
    init_session_state()
    
    # Route to appropriate screen
    if st.session_state.game_state == "welcome":
        show_welcome_screen()
    elif st.session_state.game_state == "playing":
        show_playing_screen()
    elif st.session_state.game_state == "results":
        show_results_screen()
    else:
        st.session_state.game_state = "welcome"
        st.rerun()


if __name__ == "__main__":
    main()
