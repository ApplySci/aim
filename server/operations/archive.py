# -*- coding: utf-8 -*-
"""
Tournament archiving functionality.

Handles archiving of completed tournaments, storing their data in a local database
and generating static JSON files for efficient access. This reduces load on the
Google Cloud services as the number of historic tournaments grows.

Functions:
    ensure_data_directory: Create data directory if it doesn't exist
    update_past_tournaments_json: Update static JSON file with tournament data
"""

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
from config import BASEDIR
from operations.queries import get_past_tournament_summaries
from operations.transforms import tournaments_to_summaries
import os
from write_sheet import googlesheet

PAST_TOURNAMENTS_FILE = os.path.join(BASEDIR, "data", "past_tournaments.json")


def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs(os.path.dirname(PAST_TOURNAMENTS_FILE), exist_ok=True)


def update_past_tournaments_json(tournaments: list[Tournament]) -> None:
    """Update the static JSON file containing past tournament data"""
    ensure_data_directory()
    summaries = tournaments_to_summaries(tournaments)

    with open(PAST_TOURNAMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump({"tournaments": summaries}, f, ensure_ascii=False, indent=2)

    # Update the last_updated timestamp in Firestore
    firestore_client.collection("metadata").document("past_tournaments").set(
        {"last_updated": firestore.SERVER_TIMESTAMP}, merge=True
    )


def find_matching_player(
    name: str, tournament_id: int, threshold: float = 1.1
) -> ArchivedPlayer | None:
    """Find existing player with matching name using fuzzy matching"""
    # Get players created before this tournament's archival process started
    players = (
        db.session.query(ArchivedPlayer)
        .outerjoin(TournamentPlayer)
        .filter(
            (TournamentPlayer.tournament_id != tournament_id)
            | (TournamentPlayer.tournament_id.is_(None))
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

    # Get additional data from firebase
    v3_collection = tournament_ref.collection("v3")
    ranking_doc = v3_collection.document("ranking").get().to_dict()
    scores_doc = v3_collection.document("scores").get().to_dict()
    seating_doc = v3_collection.document("seating").get().to_dict()

    # Get player data from Google Sheet (authoritative source)
    try:
        sheet = googlesheet.get_sheet(tournament.google_doc_id)
        batch_data = googlesheet.batch_get_tournament_data(sheet)
        raw_players = googlesheet.get_players_from_batch(batch_data)

        # Convert raw player data to the format expected by the rest of the function
        players_data = {"players": []}
        for p in raw_players:
            if len(p) >= 3:  # Ensure we have at least seating_id, registration_id, name
                players_data["players"].append(
                    {
                        "seating_id": p[0] if p[0] != "" else None,
                        "registration_id": str(p[1]),
                        "name": p[2],
                        "is_current": p[0] != "",
                    }
                )

        logging.info(
            f"Retrieved {len(players_data['players'])} players from Google Sheet for archiving"
        )

    except Exception as e:
        logging.error(f"Failed to get players from Google Sheet: {str(e)}")
        # Fallback to Firebase data if Google Sheet is inaccessible
        players_doc = v3_collection.document("players").get().to_dict()
        players_data = players_doc if players_doc else {"players": []}
        logging.warning("Using Firebase player data as fallback")

    # Merge all data
    tournament_data.update(
        {
            "players": players_data,
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

            # Handle None seating_id for substitute players
            seating_id = p["seating_id"]
            if seating_id is None:
                # Skip players without seating_id (substitutes who were never seated)
                logging.info(
                    f"Skipping player {p['name']} with no seating_id (likely substitute)"
                )
                continue

            tournament_player = TournamentPlayer(
                tournament=tournament,
                player=player,
                seating_id=seating_id,
                registration_id=p["registration_id"],
            )
            db.session.add(tournament_player)
            if seating_id:
                player_map[int(seating_id)] = tournament_player

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
            metadata_ref,
            {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "api_base_url": "https://wr.mahjong.ie",
            },
            merge=True,
        )

        batch.commit()
        db.session.commit()

        # After successful archival, update the JSON file
        past_tournaments = get_past_tournament_summaries()
        update_past_tournaments_json(past_tournaments)

        return stats

    except Exception as e:
        db.session.rollback()
        logging.error(e, exc_info=True)
        return False
