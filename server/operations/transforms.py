import json
from datetime import datetime
from models import Tournament

def tournament_to_summary(tournament: Tournament) -> dict:
    """Convert a tournament to its summary representation"""
    if not tournament.past_data:
        return {}
        
    stored_data = json.loads(tournament.past_data.data)
    return {
        "id": tournament.firebase_doc,
        "name": tournament.title,
        "start_date": stored_data.get("start_date"),
        "end_date": stored_data.get("end_date"),
        "venue": stored_data.get("address"),
        "country": stored_data.get("country"),
        "rules": stored_data.get("rules"),
        "player_count": len(stored_data.get("players", {}).get("players", [])),
    }

def tournaments_to_summaries(tournaments: list[Tournament]) -> list[dict]:
    """Convert a list of tournaments to their summary representations, sorted by start date (most recent first)"""
    summaries = [
        tournament_to_summary(t)
        for t in tournaments
        if t.past_data
    ]
    
    # Sort by start_date in descending order (most recent first)
    # Handle cases where start_date might be None or in different formats
    def get_sort_key(summary):
        start_date = summary.get("start_date")
        if not start_date:
            return datetime.min  # Put tournaments without dates at the end
        
        # Handle both string and datetime formats
        if isinstance(start_date, str):
            try:
                # Try parsing ISO format first
                return datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    # Try other common formats if needed
                    return datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    return datetime.min
        elif hasattr(start_date, 'year'):  # datetime-like object
            return start_date
        else:
            return datetime.min
    
    summaries.sort(key=get_sort_key, reverse=True)
    return summaries