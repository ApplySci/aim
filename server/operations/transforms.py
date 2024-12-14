import json
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
    """Convert a list of tournaments to their summary representations"""
    return [
        tournament_to_summary(t)
        for t in tournaments
        if t.past_data
    ] 