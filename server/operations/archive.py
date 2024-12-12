from datetime import datetime
import json
from firebase_admin import firestore
from oauth_setup import db, firestore_client
from models import Tournament, PastTournamentData

def archive_tournament(tournament: Tournament) -> bool:
    """Archive a tournament's data and update its status"""
    tournament_ref = firestore_client.collection("tournaments").document(tournament.firebase_doc)
    tournament_data = tournament_ref.get().to_dict()
    
    if not tournament_data:
        return False
        
    # Store the data locally
    past_data = PastTournamentData(
        tournament_id=tournament.id,
        data=json.dumps(tournament_data),
        archived_at=datetime.utcnow(),
    )
    db.session.add(past_data)
    
    # Remove data from Firestore and update metadata
    batch = firestore_client.batch()
    # TODO don't do this until we're sure we're storing it locally, properly.
    #      batch.delete(tournament_ref)
    
    metadata_ref = firestore_client.collection("metadata").document("past_tournaments")
    batch.set(metadata_ref, {"last_updated": firestore.SERVER_TIMESTAMP}, merge=True)
    
    try:
        batch.commit()
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False 