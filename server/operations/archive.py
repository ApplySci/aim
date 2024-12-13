from datetime import datetime, timezone
import json
import jellyfish
from firebase_admin import firestore
from oauth_setup import db, firestore_client, logging
from models import (
    Tournament,
    PastTournamentData,
    ArchivedPlayer,
    TournamentPlayer,
    Hanchan,
)


def find_matching_player(name: str, tournament_id: int, threshold: float = 1.1) -> ArchivedPlayer | None:
    """Find existing player with matching name using fuzzy matching"""
    # Get players created before this tournament's archival process started
    players = (
        db.session.query(ArchivedPlayer)
        .outerjoin(TournamentPlayer)
        .filter(
            (TournamentPlayer.tournament_id != tournament_id) | 
            (TournamentPlayer.tournament_id.is_(None))
        )
        .all()
    )

    best_match = None
    best_score = threshold

    for player in players:
        score = jellyfish.damerau_levenshtein_distance(
            name.lower(), player.name.lower()
        )
        if score < threshold:
            logging.info(f'find_matching_player matches "{name}" with "{player.name}"')
            if score < best_score:
                best_match = player
                best_score = score

    return best_match


def archive_tournament(tournament: Tournament) -> dict | bool:
    """Archive a tournament's data and update its status"""
    # Get main tournament document
    tournament_ref = firestore_client.collection("tournaments").document(
        tournament.firebase_doc
    )
    tournament_data = tournament_ref.get().to_dict()

    if not tournament_data:
        return False

    # Get additional data from v3 subcollection
    v3_collection = tournament_ref.collection("v3")
    players_doc = v3_collection.document("players").get().to_dict()
    ranking_doc = v3_collection.document("ranking").get().to_dict()
    scores_doc = v3_collection.document("scores").get().to_dict()
    seating_doc = v3_collection.document("seating").get().to_dict()

    # Merge all data
    tournament_data.update(
        {
            "players": players_doc,
            "ranking": ranking_doc,
            "scores": scores_doc,
            "seating": seating_doc,
        }
    )

    # Process and store structured data
    try:
        # Convert datetime objects to ISO format strings
        if "end_date" in tournament_data:
            tournament_data["end_date"] = tournament_data["end_date"].isoformat()
        if "start_date" in tournament_data:
            tournament_data["start_date"] = tournament_data["start_date"].isoformat()

        data = json.dumps(tournament_data)
        # Store raw data
        past_data = PastTournamentData(
            tournament_id=tournament.id,
            data=data,
            archived_at=datetime.now(timezone.utc),
        )
        db.session.add(past_data)

        # Archive players
        stats = {
            "new_players": 0,
            "exact_matches": 0,
            "fuzzy_matches": [],
        }

        player_map = {}
        for p in tournament_data.get("players", {}).get("players", []):
            # First try exact match
            player = db.session.query(ArchivedPlayer).filter_by(name=p["name"]).first()
            if player:
                stats["exact_matches"] += 1
            else:
                # Try fuzzy match against existing players from other tournaments
                player = find_matching_player(p["name"], tournament.id)
                if player:
                    stats["fuzzy_matches"].append(
                        {"tournament_name": p["name"], "matched_name": player.name}
                    )
                else:
                    # Create new player
                    player = ArchivedPlayer(name=p["name"])
                    db.session.add(player)
                    stats["new_players"] += 1

            tournament_player = TournamentPlayer(
                tournament=tournament,
                player=player,
                seating_id=p["seating_id"],
                registration_id=p["registration_id"],
            )
            db.session.add(tournament_player)
            if p["seating_id"]:
                player_map[int(p["seating_id"])] = tournament_player

        # Archive game results
        scores = tournament_data.get("scores", {})
        for hanchan_num, tables in scores.items():
            if hanchan_num == "roundDone":
                continue

            for table_num, seats in tables.items():
                if table_num == "missing":
                    continue

                for seat_num, result in seats.items():
                    player_id = result[0]
                    if player_id not in player_map:
                        logging.warning(f"    No mapping found for player {player_id}")
                        continue
                    hanchan_result = Hanchan(
                        tournament=tournament,
                        player=player_map[player_id],
                        hanchan_number=int(hanchan_num),
                        table_number=table_num,
                        seat=int(seat_num),
                        points=result[2],
                        placement=result[3],
                        chombo=result[1],
                    )
                    db.session.add(hanchan_result)

        # Remove data from Firestore and update metadata
        batch = firestore_client.batch()
        # batch.delete(tournament_ref)

        metadata_ref = firestore_client.collection("metadata").document(
            "past_tournaments"
        )
        batch.set(
            metadata_ref, {"last_updated": firestore.SERVER_TIMESTAMP}, merge=True
        )

        batch.commit()
        db.session.commit()
        return stats

    except Exception as e:
        db.session.rollback()
        logging.error(e, exc_info=True)
        return False
