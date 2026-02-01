"""
Audio analysis module for Scam School game.
Adapted from speech_to_text_llm for game scoring context.
"""

import json
import os
import tempfile
from dataclasses import dataclass
from typing import List, Optional

import librosa
import numpy as np
import soundfile as sf
from openai import OpenAI

# Sample rate for audio processing
SAMPLE_RATE = 16000  # Whisper works well with 16kHz


@dataclass
class AudioCharacteristics:
    """Meta characteristics extracted from audio."""
    average_pitch: float  # Hz
    pitch_variance: float  # Variability in pitch
    speaking_rate: float  # Energy changes per second (proxy for speech rate)
    tempo: float  # BPM-like measure
    spectral_centroid: float  # Brightness/timbre
    zero_crossing_rate: float  # Roughness/noisiness
    energy_mean: float  # Average volume/energy
    energy_variance: float  # Volume variation
    duration: float  # seconds


@dataclass
class VoiceBreakdown:
    """Detailed voice score breakdown."""
    urgency: int        # 0-25: Pressure and time sensitivity in delivery
    authority: int      # 0-25: Confidence and commanding presence
    emotion: int        # 0-25: Emotional manipulation and expressiveness
    pacing: int         # 0-25: Speed variation and dramatic timing
    
    @property
    def total(self) -> int:
        return self.urgency + self.authority + self.emotion + self.pacing


@dataclass
class BonusScores:
    """Bonus point categories."""
    improvisation: int  # 0-20: Added convincing details beyond script
    accuracy: int       # 0-20: How closely followed the script
    style: int          # 0-10: Accents, commitment, character
    
    @property
    def total(self) -> int:
        return self.improvisation + self.accuracy + self.style


@dataclass
class GameScore:
    """Complete game score with detailed breakdown."""
    # Main scores
    content_score: int  # 0-100
    voice_breakdown: VoiceBreakdown  # Detailed voice scores (max 100)
    bonus_scores: BonusScores  # Bonus points (max 50)
    
    # Computed totals
    voice_score: int  # Sum of voice breakdown (0-100)
    bonus_total: int  # Sum of bonus scores (0-50)
    total_score: int  # Grand total (0-250)
    
    # Feedback
    content_feedback: str
    voice_feedback: str
    pro_tips: List[str]  # Specific improvement suggestions
    
    # Data
    transcript: str
    characteristics: AudioCharacteristics
    title: str  # Player ranking title


def get_title_for_score(score: int) -> str:
    """Get a fun title based on total score (now 0-250 scale)."""
    if score <= 50:
        return "Honest Citizen"
    elif score <= 100:
        return "Suspicious Caller"
    elif score <= 150:
        return "Amateur Con Artist"
    elif score <= 200:
        return "Professional Grifter"
    else:
        return "Master Scammer"


def analyze_audio_characteristics(audio: np.ndarray, sr: int) -> AudioCharacteristics:
    """Extract meta characteristics from audio."""
    
    # Duration
    duration = len(audio) / sr
    
    # Ensure audio is not empty
    if len(audio) == 0 or duration < 0.1:
        return AudioCharacteristics(
            average_pitch=0.0,
            pitch_variance=0.0,
            speaking_rate=0.0,
            tempo=0.0,
            spectral_centroid=0.0,
            zero_crossing_rate=0.0,
            energy_mean=0.0,
            energy_variance=0.0,
            duration=duration
        )
    
    # Pitch estimation
    pitches, magnitudes = librosa.piptrack(y=audio, sr=sr, threshold=0.1)
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            pitch_values.append(pitch)
    
    if pitch_values:
        average_pitch = float(np.mean(pitch_values))
        pitch_variance = float(np.var(pitch_values))
    else:
        average_pitch = 0.0
        pitch_variance = 0.0
    
    # Tempo estimation
    tempo_result, _ = librosa.beat.beat_track(y=audio, sr=sr)
    tempo = float(tempo_result[0]) if hasattr(tempo_result, '__len__') else float(tempo_result)
    
    # Spectral features
    spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
    spectral_centroid_mean = float(np.mean(spectral_centroids))
    
    # Zero crossing rate
    zcr = librosa.feature.zero_crossing_rate(audio)[0]
    zcr_mean = float(np.mean(zcr))
    
    # RMS energy (volume)
    rms = librosa.feature.rms(y=audio)[0]
    energy_mean = float(np.mean(rms))
    energy_variance = float(np.var(rms))
    
    # Speaking rate (energy changes as proxy)
    energy_changes = np.sum(np.diff(rms > np.percentile(rms, 50)) != 0)
    speaking_rate = energy_changes / duration if duration > 0 else 0.0
    
    return AudioCharacteristics(
        average_pitch=average_pitch,
        pitch_variance=pitch_variance,
        speaking_rate=speaking_rate,
        tempo=tempo,
        spectral_centroid=spectral_centroid_mean,
        zero_crossing_rate=zcr_mean,
        energy_mean=energy_mean,
        energy_variance=energy_variance,
        duration=duration
    )


def transcribe_audio(client: OpenAI, audio_path: str) -> str:
    """Convert audio to text using OpenAI Whisper API."""
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return transcript


def analyze_performance(
    client: OpenAI,
    transcript: str,
    characteristics: AudioCharacteristics,
    original_prompt: str,
    difficulty: str
) -> dict:
    """
    Analyze the player's scam performance using GPT-4o.
    Returns detailed scores, breakdown, and feedback for the game.
    """
    
    char_desc = f"""
Voice Characteristics (measured from audio):
- Average Pitch: {characteristics.average_pitch:.2f} Hz
- Pitch Variance: {characteristics.pitch_variance:.2f} (variation in tone)
- Speaking Rate: {characteristics.speaking_rate:.2f} (energy changes per second)
- Tempo: {characteristics.tempo:.2f} BPM
- Voice Brightness: {characteristics.spectral_centroid:.2f} Hz
- Voice Energy: {characteristics.energy_mean:.4f} (average volume)
- Energy Variation: {characteristics.energy_variance:.6f} (volume dynamics)
- Duration: {characteristics.duration:.2f} seconds
"""
    
    prompt = f"""You are a judge for a fun party game called "Scam School" where players try to deliver the most convincing scam call performance. This is purely for entertainment - players are voice acting, not actually scamming anyone.

The player was given this scam script to read ({difficulty} difficulty):
---
{original_prompt}
---

Here's what they actually said (transcribed):
---
{transcript}
---

{char_desc}

Score their PERFORMANCE with detailed breakdown:

## 1. CONTENT SCORE (0-100)
How well did they deliver the scam script content?

## 2. VOICE BREAKDOWN (each 0-25, total 100)
- **Urgency**: Pressure and time sensitivity in their delivery
- **Authority**: Confidence and commanding presence
- **Emotion**: Emotional manipulation and expressiveness
- **Pacing**: Speed variation and dramatic timing

## 3. BONUS SCORES
- **Improvisation (0-20)**: Did they add convincing details beyond the script?
- **Accuracy (0-20)**: How closely did they follow the original script?
- **Style (0-10)**: Accents, character commitment, extra flair

## 4. PRO TIPS
Give 2-3 specific, actionable tips to improve their performance.

Be generous but fair - this is a fun game! Give specific, entertaining feedback.

Respond with a JSON object:
{{
    "content_score": <0-100>,
    "content_feedback": "<2-3 sentences about their script delivery>",
    "voice_breakdown": {{
        "urgency": <0-25>,
        "authority": <0-25>,
        "emotion": <0-25>,
        "pacing": <0-25>
    }},
    "voice_feedback": "<2-3 sentences about their vocal performance>",
    "bonus_scores": {{
        "improvisation": <0-20>,
        "accuracy": <0-20>,
        "style": <0-10>
    }},
    "pro_tips": [
        "<specific tip 1>",
        "<specific tip 2>",
        "<specific tip 3>"
    ]
}}
"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a fun, entertaining game judge for Scam School. Give detailed scores and playful feedback. Use humor! Always provide exactly 3 pro tips."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )
    
    result = json.loads(response.choices[0].message.content)
    return result


def process_audio_for_game(
    audio_bytes: bytes,
    original_prompt: str,
    difficulty: str,
    api_key: str
) -> GameScore:
    """
    Main function to process recorded audio and return game scores.
    
    Args:
        audio_bytes: Raw audio data (WAV format)
        original_prompt: The scam script the player was supposed to read
        difficulty: Difficulty level (easy/medium/hard)
        api_key: OpenAI API key
    
    Returns:
        GameScore with all results including detailed breakdown
    """
    client = OpenAI(api_key=api_key)
    
    # Save audio to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        tmp_file.write(audio_bytes)
    
    try:
        # Load audio for analysis
        audio, sr = librosa.load(tmp_path, sr=SAMPLE_RATE)
        
        # Step 1: Transcribe
        transcript = transcribe_audio(client, tmp_path)
        
        # Step 2: Analyze voice characteristics
        characteristics = analyze_audio_characteristics(audio, sr)
        
        # Step 3: Get GPT scoring with detailed breakdown
        results = analyze_performance(
            client, transcript, characteristics, original_prompt, difficulty
        )
        
        # Parse results
        content_score = int(results.get("content_score", 50))
        
        # Voice breakdown
        vb = results.get("voice_breakdown", {})
        voice_breakdown = VoiceBreakdown(
            urgency=int(vb.get("urgency", 12)),
            authority=int(vb.get("authority", 12)),
            emotion=int(vb.get("emotion", 12)),
            pacing=int(vb.get("pacing", 12))
        )
        
        # Bonus scores
        bs = results.get("bonus_scores", {})
        bonus_scores = BonusScores(
            improvisation=int(bs.get("improvisation", 10)),
            accuracy=int(bs.get("accuracy", 10)),
            style=int(bs.get("style", 5))
        )
        
        # Calculate totals
        voice_score = voice_breakdown.total
        bonus_total = bonus_scores.total
        total_score = content_score + voice_score + bonus_total
        
        # Pro tips
        pro_tips = results.get("pro_tips", ["Keep practicing!", "Try adding more emotion!", "Great start!"])
        if not isinstance(pro_tips, list):
            pro_tips = [pro_tips]
        
        return GameScore(
            content_score=content_score,
            voice_breakdown=voice_breakdown,
            bonus_scores=bonus_scores,
            voice_score=voice_score,
            bonus_total=bonus_total,
            total_score=total_score,
            content_feedback=results.get("content_feedback", "Great attempt!"),
            voice_feedback=results.get("voice_feedback", "Nice vocal work!"),
            pro_tips=pro_tips,
            transcript=transcript,
            characteristics=characteristics,
            title=get_title_for_score(total_score)
        )
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def process_audio_file_for_game(
    audio_path: str,
    original_prompt: str,
    difficulty: str,
    api_key: str
) -> GameScore:
    """
    Process an audio file and return game scores.
    Alternative to process_audio_for_game when you have a file path.
    """
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    return process_audio_for_game(audio_bytes, original_prompt, difficulty, api_key)
