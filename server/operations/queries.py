from typing import List, Optional
from sqlalchemy import select, func
from oauth_setup import db
from models import (
    Tournament,
    PastTournamentData,
    ArchivedPlayer,
    TournamentPlayer,
    Hanchan,
)


def get_past_tournament_summaries() -> List[Tournament]:
    """Get all past tournaments with their data"""
    return db.session.query(Tournament).join(PastTournamentData).all()


def get_past_tournament_details(firebase_id: str) -> Optional[Tournament]:
    """Get a specific past tournament with its data"""
    return (
        db.session.query(Tournament)
        .filter_by(firebase_doc=firebase_id)
        .join(PastTournamentData)
        .first()
    )


def get_player_tournament_history(player_id: int) -> List[dict]:
    """Get all tournament results for a player"""
    results = (
        db.session.query(
            Tournament.title,
            Tournament.firebase_doc,
            func.count(Hanchan.id).label("hanchan_count"),
            func.avg(Hanchan.points).label("avg_points"),
            func.avg(Hanchan.placement).label("avg_placement"),
        )
        .join(Hanchan.tournament)
        .join(Hanchan.player)
        .filter(TournamentPlayer.player_id == player_id)
        .group_by(Tournament.id)
        .all()
    )

    return [
        {
            "tournament_name": r.title,
            "tournament_id": r.firebase_doc,
            "hanchan_count": r.hanchan_count,
            "avg_points": float(r.avg_points),
            "avg_placement": float(r.avg_placement),
        }
        for r in results
    ]


def get_tournament_results(tournament_id: int) -> List[dict]:
    """Get detailed results for all players in a tournament"""
    results = (
        db.session.query(
            ArchivedPlayer.name,
            func.count(Hanchan.id).label("hanchan_count"),
            func.avg(Hanchan.points).label("avg_points"),
            func.avg(Hanchan.placement).label("avg_placement"),
        )
        .join(TournamentPlayer, ArchivedPlayer.tournament_appearances)
        .join(Hanchan, TournamentPlayer.results)
        .filter(TournamentPlayer.tournament_id == tournament_id)
        .group_by(ArchivedPlayer.id)
        .all()
    )

    return [
        {
            "player_name": r.name,
            "hanchan_count": r.hanchan_count,
            "avg_points": float(r.avg_points),
            "avg_placement": float(r.avg_placement),
        }
        for r in results
    ]
