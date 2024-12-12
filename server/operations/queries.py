from typing import List, Optional
from sqlalchemy import select
from oauth_setup import db
from models import Tournament, PastTournamentData

def get_past_tournament_summaries() -> List[Tournament]:
    """Get all past tournaments with their data"""
    return (
        db.session.query(Tournament)
        .join(PastTournamentData)
        .all()
    )

def get_past_tournament_details(firebase_id: str) -> Optional[Tournament]:
    """Get a specific past tournament with its data"""
    return (
        db.session.query(Tournament)
        .filter_by(firebase_doc=firebase_id)
        .join(PastTournamentData)
        .first()
    ) 