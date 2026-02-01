"""
Leaderboard management for Scam School game.
Handles score storage and retrieval.
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional

# Default leaderboard file path
LEADERBOARD_FILE = "leaderboard.json"


@dataclass
class LeaderboardEntry:
    """A single entry on the leaderboard."""
    player_name: str
    total_score: int
    content_score: int
    voice_score: int
    title: str
    difficulty: str
    category: str
    timestamp: str
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "LeaderboardEntry":
        return cls(**data)


class Leaderboard:
    """Manages the game leaderboard."""
    
    def __init__(self, file_path: str = LEADERBOARD_FILE):
        self.file_path = file_path
        self.entries: List[LeaderboardEntry] = []
        self.load()
    
    def load(self) -> None:
        """Load leaderboard from file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.entries = [LeaderboardEntry.from_dict(e) for e in data]
            except (json.JSONDecodeError, KeyError):
                self.entries = []
        else:
            self.entries = []
    
    def save(self) -> None:
        """Save leaderboard to file."""
        with open(self.file_path, "w") as f:
            json.dump([e.to_dict() for e in self.entries], f, indent=2)
    
    def add_entry(
        self,
        player_name: str,
        total_score: int,
        content_score: int,
        voice_score: int,
        title: str,
        difficulty: str,
        category: str
    ) -> LeaderboardEntry:
        """Add a new entry to the leaderboard."""
        entry = LeaderboardEntry(
            player_name=player_name,
            total_score=total_score,
            content_score=content_score,
            voice_score=voice_score,
            title=title,
            difficulty=difficulty,
            category=category,
            timestamp=datetime.now().isoformat()
        )
        self.entries.append(entry)
        self.entries.sort(key=lambda x: x.total_score, reverse=True)
        self.save()
        return entry
    
    def get_top_scores(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top N scores."""
        return self.entries[:limit]
    
    def get_scores_by_difficulty(self, difficulty: str, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top scores for a specific difficulty."""
        filtered = [e for e in self.entries if e.difficulty.lower() == difficulty.lower()]
        return filtered[:limit]
    
    def get_player_best(self, player_name: str) -> Optional[LeaderboardEntry]:
        """Get a player's best score."""
        player_entries = [e for e in self.entries if e.player_name.lower() == player_name.lower()]
        if player_entries:
            return max(player_entries, key=lambda x: x.total_score)
        return None
    
    def get_player_rank(self, player_name: str) -> Optional[int]:
        """Get a player's rank (1-indexed)."""
        best = self.get_player_best(player_name)
        if best:
            for i, entry in enumerate(self.entries):
                if entry.player_name.lower() == player_name.lower() and entry.total_score == best.total_score:
                    return i + 1
        return None
    
    def clear(self) -> None:
        """Clear all entries."""
        self.entries = []
        self.save()
    
    def get_stats(self) -> dict:
        """Get leaderboard statistics."""
        if not self.entries:
            return {
                "total_games": 0,
                "average_score": 0,
                "highest_score": 0,
                "unique_players": 0
            }
        
        return {
            "total_games": len(self.entries),
            "average_score": sum(e.total_score for e in self.entries) / len(self.entries),
            "highest_score": max(e.total_score for e in self.entries),
            "unique_players": len(set(e.player_name.lower() for e in self.entries))
        }


def format_leaderboard_table(entries: List[LeaderboardEntry]) -> str:
    """Format leaderboard entries as a nice table string."""
    if not entries:
        return "No scores yet! Be the first to play!"
    
    lines = ["| Rank | Player | Score | Title | Difficulty |",
             "|------|--------|-------|-------|------------|"]
    
    for i, entry in enumerate(entries, 1):
        lines.append(
            f"| {i} | {entry.player_name} | {entry.total_score}/200 | {entry.title} | {entry.difficulty.title()} |"
        )
    
    return "\n".join(lines)
