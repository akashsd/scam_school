"""
Scam School - Voice Acting Challenge Game
A fun party game where you try to sound like a convincing scammer!
"""

import os
import streamlit as st
import plotly.graph_objects as go

from analysis import process_audio_for_game, GameScore, VoiceBreakdown, BonusScores
from prompts import get_random_prompt, ScamPrompt
from leaderboard import Leaderboard, format_leaderboard_table


def get_api_key():
    """Get OpenAI API key from Streamlit secrets or environment."""
    try:
        return st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass
    return os.environ.get("OPENAI_API_KEY")


# Page config
st.set_page_config(
    page_title="Scam School",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobile-optimized CSS
st.markdown("""
<style>
    /* Base styles */
    .main-title {
        text-align: center;
        color: #FF4B4B;
        font-size: 2.5em;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-top: 0;
    }
    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 15px;
        color: white;
        text-align: center;
        margin: 8px 0;
    }
    .big-score {
        font-size: 3em;
        font-weight: bold;
        margin: 0;
    }
    .title-badge {
        background: gold;
        color: black;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 8px 0;
    }
    .prompt-box {
        background: #1a1a2e;
        color: #eee;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #FF4B4B;
        font-family: monospace;
        font-size: 1em;
        line-height: 1.5;
    }
    .tip-box {
        background: #fff3cd;
        color: #856404;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
    }
    .pro-tip {
        background: #d4edda;
        color: #155724;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid #28a745;
    }
    .player-turn {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 15px 0;
    }
    .winner-box {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: black;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 15px 0;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-title { font-size: 1.8em; }
        .big-score { font-size: 2.5em; }
        .prompt-box { font-size: 0.9em; padding: 12px; }
        .score-box { padding: 12px; }
    }
    
    /* Touch-friendly buttons */
    .stButton > button {
        min-height: 48px;
        touch-action: manipulation;
        font-size: 1em;
    }
    
    /* Prevent zoom on input focus (iOS) */
    input, select, textarea {
        font-size: 16px !important;
    }
    
    /* Mode selection cards */
    .mode-card {
        background: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    .mode-card:hover {
        border-color: #FF4B4B;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "game_state" not in st.session_state:
        st.session_state.game_state = "mode_select"
    if "game_mode" not in st.session_state:
        st.session_state.game_mode = "single"
    if "player_name" not in st.session_state:
        st.session_state.player_name = ""
    if "players" not in st.session_state:
        st.session_state.players = []
    if "current_player_idx" not in st.session_state:
        st.session_state.current_player_idx = 0
    if "player_scores" not in st.session_state:
        st.session_state.player_scores = {}
    if "current_prompt" not in st.session_state:
        st.session_state.current_prompt = None
    if "multiplayer_prompt" not in st.session_state:
        st.session_state.multiplayer_prompt = None
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "medium"
    if "last_score" not in st.session_state:
        st.session_state.last_score = None
    if "leaderboard" not in st.session_state:
        st.session_state.leaderboard = Leaderboard()


def create_radar_chart(voice_breakdown: VoiceBreakdown) -> go.Figure:
    """Create a radar chart for voice breakdown scores."""
    categories = ['Urgency', 'Authority', 'Emotion', 'Pacing']
    values = [
        voice_breakdown.urgency,
        voice_breakdown.authority,
        voice_breakdown.emotion,
        voice_breakdown.pacing
    ]
    # Close the polygon
    values.append(values[0])
    categories.append(categories[0])
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.5)',
        line=dict(color='#667eea', width=2),
        marker=dict(size=8, color='#764ba2')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 25],
                tickvals=[5, 10, 15, 20, 25],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=12)
            )
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def show_mode_selection():
    """Display mode selection screen."""
    st.markdown('<h1 class="main-title">🎭 Scam School</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">The Voice Acting Challenge</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Choose Your Mode")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Single Player")
        st.markdown("Practice your scam skills solo and climb the leaderboard!")
        if st.button("Play Solo", use_container_width=True, type="primary"):
            st.session_state.game_mode = "single"
            st.session_state.game_state = "welcome"
            st.rerun()
    
    with col2:
        st.markdown("#### 👥 Multiplayer")
        st.markdown("Pass & play with friends - same prompt, compare scores!")
        if st.button("Play with Friends", use_container_width=True):
            st.session_state.game_mode = "multiplayer"
            st.session_state.game_state = "multiplayer_setup"
            st.rerun()
    
    # Show leaderboard preview
    st.markdown("---")
    st.markdown("### 🏆 Top Scores")
    top_scores = st.session_state.leaderboard.get_top_scores(3)
    if top_scores:
        for i, entry in enumerate(top_scores, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            st.markdown(f"{medal} **{entry.player_name}** - {entry.total_score}/250")
    else:
        st.info("No scores yet! Be the first to play!")


def show_multiplayer_setup():
    """Display multiplayer setup screen."""
    st.markdown('<h1 class="main-title">👥 Multiplayer Setup</h1>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    num_players = st.slider("Number of Players", min_value=2, max_value=6, value=2)
    
    st.markdown("### Enter Player Names")
    
    players = []
    cols = st.columns(2)
    for i in range(num_players):
        with cols[i % 2]:
            name = st.text_input(
                f"Player {i + 1}",
                key=f"player_{i}",
                placeholder=f"Player {i + 1} name..."
            )
            players.append(name.strip() if name else f"Player {i + 1}")
    
    st.markdown("---")
    
    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        index=1
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.game_state = "mode_select"
            st.rerun()
    
    with col2:
        if st.button("Start Game! 🎬", use_container_width=True, type="primary"):
            # Validate all names are filled
            valid_players = [p for p in players if p.strip()]
            if len(valid_players) < 2:
                st.error("Please enter at least 2 player names!")
            else:
                st.session_state.players = players
                st.session_state.difficulty = difficulty.lower()
                st.session_state.current_player_idx = 0
                st.session_state.player_scores = {}
                st.session_state.multiplayer_prompt = get_random_prompt(st.session_state.difficulty)
                st.session_state.game_state = "turn_transition"
                st.rerun()


def show_turn_transition():
    """Display turn transition screen between players."""
    current_player = st.session_state.players[st.session_state.current_player_idx]
    total_players = len(st.session_state.players)
    current_num = st.session_state.current_player_idx + 1
    
    st.markdown('<h1 class="main-title">🎭 Pass the Phone!</h1>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="player-turn">
        <h2 style="margin: 0;">Player {current_num} of {total_players}</h2>
        <h1 style="margin: 10px 0; font-size: 2.5em;">{current_player}</h1>
        <p style="margin: 0;">It's your turn!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚠️ No peeking at others' recordings!")
    st.markdown("Everyone gets the **same prompt** - may the best scammer win!")
    
    if st.button(f"I'm {current_player} - Start My Turn! 🎬", use_container_width=True, type="primary"):
        st.session_state.current_prompt = st.session_state.multiplayer_prompt
        st.session_state.game_state = "playing"
        st.rerun()


def show_welcome_screen():
    """Display the welcome/start screen for single player."""
    st.markdown('<h1 class="main-title">🎭 Scam School</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">The Voice Acting Challenge</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    ### How to Play
    
    1. **Enter your name** and select a difficulty
    2. **Read the scam script** you're given
    3. **Record yourself** performing the script
    4. **Get scored** on your scammer performance!
    
    *Can you sound like a convincing con artist?* 🎬
    """)
    
    st.markdown("---")
    
    # Player name input
    name = st.text_input(
        "Enter your name",
        value=st.session_state.player_name,
        placeholder="Your scammer alias..."
    )
    st.session_state.player_name = name
    
    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        index=1
    )
    st.session_state.difficulty = difficulty.lower()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.game_state = "mode_select"
            st.rerun()
    
    with col2:
        if st.button("🎬 Start Game", use_container_width=True, type="primary"):
            if st.session_state.player_name.strip():
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
            st.markdown(f"{medal} **{entry.player_name}** - {entry.total_score}/250 ({entry.title})")
    else:
        st.info("No scores yet! Be the first to play!")


def show_playing_screen():
    """Display the game playing screen with prompt and recording."""
    prompt: ScamPrompt = st.session_state.current_prompt
    
    # Show current player in multiplayer
    if st.session_state.game_mode == "multiplayer":
        current_player = st.session_state.players[st.session_state.current_player_idx]
        st.markdown(f"**🎭 {current_player}'s Turn**")
    
    st.markdown(f'<h1 class="main-title">📜 Your Script</h1>', unsafe_allow_html=True)
    
    # Compact prompt info for mobile
    st.markdown(f"**{prompt.category}** | {prompt.difficulty.title()} | *{prompt.title}*")
    
    st.markdown("---")
    
    # The scam script
    st.markdown(f'<div class="prompt-box">{prompt.script}</div>', unsafe_allow_html=True)
    
    # Acting tips
    st.markdown(f'<div class="tip-box">💡 <strong>Tip:</strong> {prompt.tips}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recording section
    st.markdown("### 🎙️ Record Your Performance")
    
    try:
        from audio_recorder_streamlit import audio_recorder
        
        audio_bytes = audio_recorder(
            text="Tap to record",
            recording_color="#FF4B4B",
            neutral_color="#6c757d",
            icon_size="2x",
            pause_threshold=15.0,
        )
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎯 Submit", use_container_width=True, type="primary"):
                    with st.spinner("🔍 Analyzing..."):
                        api_key = get_api_key()
                        if not api_key:
                            st.error("OpenAI API key not found!")
                        else:
                            try:
                                score = process_audio_for_game(
                                    audio_bytes=audio_bytes,
                                    original_prompt=prompt.script,
                                    difficulty=prompt.difficulty,
                                    api_key=api_key
                                )
                                st.session_state.last_score = score
                                
                                # Handle multiplayer vs single player
                                if st.session_state.game_mode == "multiplayer":
                                    current_player = st.session_state.players[st.session_state.current_player_idx]
                                    st.session_state.player_scores[current_player] = score
                                    st.session_state.game_state = "results"
                                else:
                                    # Add to leaderboard (single player)
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
                                st.error(f"Error: {str(e)}")
            
            with col2:
                if st.button("🔄 Re-record", use_container_width=True):
                    st.rerun()
    
    except ImportError:
        st.error("Audio recorder not available. Install: `pip install audio-recorder-streamlit`")
    
    # Back button
    st.markdown("---")
    if st.button("← Back to Menu"):
        st.session_state.game_state = "mode_select"
        st.rerun()


def show_results_screen():
    """Display the results/score screen with radar chart."""
    score: GameScore = st.session_state.last_score
    
    # Show player name in multiplayer
    if st.session_state.game_mode == "multiplayer":
        current_player = st.session_state.players[st.session_state.current_player_idx]
        st.markdown(f"### 🎭 {current_player}'s Results")
    
    st.markdown('<h1 class="main-title">🎉 Results!</h1>', unsafe_allow_html=True)
    
    # Big score display
    st.markdown(f"""
    <div class="score-box">
        <p class="big-score">{score.total_score}</p>
        <p style="font-size: 1.2em; margin: 0;">out of 250</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Title badge
    st.markdown(f"""
    <div style="text-align: center;">
        <span class="title-badge">🏅 {score.title}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Score breakdown in tabs for mobile
    tab1, tab2, tab3 = st.tabs(["📊 Voice", "📝 Content", "⭐ Bonus"])
    
    with tab1:
        # Radar chart
        fig = create_radar_chart(score.voice_breakdown)
        st.plotly_chart(fig, use_container_width=True)
        
        # Voice breakdown numbers
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Urgency", f"{score.voice_breakdown.urgency}/25")
            st.metric("Authority", f"{score.voice_breakdown.authority}/25")
        with col2:
            st.metric("Emotion", f"{score.voice_breakdown.emotion}/25")
            st.metric("Pacing", f"{score.voice_breakdown.pacing}/25")
        
        st.markdown(f"**Total Voice Score: {score.voice_score}/100**")
        st.markdown(f"*{score.voice_feedback}*")
    
    with tab2:
        st.progress(score.content_score / 100)
        st.markdown(f"### {score.content_score}/100")
        st.markdown(f"*{score.content_feedback}*")
    
    with tab3:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Improv", f"{score.bonus_scores.improvisation}/20")
        with col2:
            st.metric("Accuracy", f"{score.bonus_scores.accuracy}/20")
        with col3:
            st.metric("Style", f"{score.bonus_scores.style}/10")
        
        st.markdown(f"**Total Bonus: {score.bonus_total}/50**")
    
    # Pro Tips
    st.markdown("---")
    st.markdown("### 💡 Pro Tips")
    for tip in score.pro_tips:
        st.markdown(f'<div class="pro-tip">{tip}</div>', unsafe_allow_html=True)
    
    # Transcript expander
    with st.expander("📜 What you said"):
        st.markdown(f"> {score.transcript}")
    
    st.markdown("---")
    
    # Action buttons based on mode
    if st.session_state.game_mode == "multiplayer":
        # Check if more players
        if st.session_state.current_player_idx < len(st.session_state.players) - 1:
            if st.button("➡️ Next Player's Turn", use_container_width=True, type="primary"):
                st.session_state.current_player_idx += 1
                st.session_state.game_state = "turn_transition"
                st.rerun()
        else:
            if st.button("🏆 See Final Results!", use_container_width=True, type="primary"):
                st.session_state.game_state = "final_comparison"
                st.rerun()
    else:
        # Single player buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎬 Play Again", use_container_width=True, type="primary"):
                st.session_state.current_prompt = get_random_prompt(st.session_state.difficulty)
                st.session_state.game_state = "playing"
                st.rerun()
        
        with col2:
            if st.button("🏠 Menu", use_container_width=True):
                st.session_state.game_state = "mode_select"
                st.rerun()
        
        rank = st.session_state.leaderboard.get_player_rank(st.session_state.player_name)
        if rank:
            st.success(f"🏆 You're ranked #{rank} on the leaderboard!")


def show_final_comparison():
    """Display final multiplayer comparison screen."""
    st.markdown('<h1 class="main-title">🏆 Final Results!</h1>', unsafe_allow_html=True)
    
    # Sort players by score
    sorted_players = sorted(
        st.session_state.player_scores.items(),
        key=lambda x: x[1].total_score,
        reverse=True
    )
    
    # Winner announcement
    winner_name, winner_score = sorted_players[0]
    st.markdown(f"""
    <div class="winner-box">
        <h3 style="margin: 0;">👑 WINNER 👑</h3>
        <h1 style="margin: 10px 0; font-size: 2em;">{winner_name}</h1>
        <h2 style="margin: 0;">{winner_score.total_score} points</h2>
        <p style="margin: 5px 0;">{winner_score.title}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📊 All Scores")
    
    # Show all player scores
    for i, (player_name, score) in enumerate(sorted_players):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
        
        with st.expander(f"{medal} {player_name} - {score.total_score}/250", expanded=(i == 0)):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Content", f"{score.content_score}/100")
            with col2:
                st.metric("Voice", f"{score.voice_score}/100")
            with col3:
                st.metric("Bonus", f"{score.bonus_total}/50")
            
            # Mini radar chart
            fig = create_radar_chart(score.voice_breakdown)
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
    
    # Add winner to leaderboard
    st.session_state.leaderboard.add_entry(
        player_name=winner_name,
        total_score=winner_score.total_score,
        content_score=winner_score.content_score,
        voice_score=winner_score.voice_score,
        title=winner_score.title,
        difficulty=st.session_state.difficulty,
        category=st.session_state.multiplayer_prompt.category
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Rematch!", use_container_width=True, type="primary"):
            st.session_state.current_player_idx = 0
            st.session_state.player_scores = {}
            st.session_state.multiplayer_prompt = get_random_prompt(st.session_state.difficulty)
            st.session_state.game_state = "turn_transition"
            st.rerun()
    
    with col2:
        if st.button("🏠 Main Menu", use_container_width=True):
            st.session_state.game_state = "mode_select"
            st.session_state.game_mode = "single"
            st.session_state.players = []
            st.session_state.player_scores = {}
            st.rerun()


def main():
    """Main app entry point."""
    init_session_state()
    
    # Route to appropriate screen
    if st.session_state.game_state == "mode_select":
        show_mode_selection()
    elif st.session_state.game_state == "multiplayer_setup":
        show_multiplayer_setup()
    elif st.session_state.game_state == "turn_transition":
        show_turn_transition()
    elif st.session_state.game_state == "welcome":
        show_welcome_screen()
    elif st.session_state.game_state == "playing":
        show_playing_screen()
    elif st.session_state.game_state == "results":
        show_results_screen()
    elif st.session_state.game_state == "final_comparison":
        show_final_comparison()
    else:
        st.session_state.game_state = "mode_select"
        st.rerun()


if __name__ == "__main__":
    main()
