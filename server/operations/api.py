from flask import Blueprint, jsonify
import json

from operations.queries import get_past_tournament_summaries, get_past_tournament_details
from operations.transforms import tournaments_to_summaries
from operations.archive import update_past_tournaments_json, PAST_TOURNAMENTS_FILE

blueprint = Blueprint("api", __name__)


@blueprint.route("/api/tournament/<tournament_id>", methods=["GET"])
def get_tournament_details(tournament_id):
    tournament = get_past_tournament_details(tournament_id)

    if not tournament or not tournament.past_data:
        return jsonify({"error": "Tournament not found"}), 404

    stored_data = json.loads(tournament.past_data.data)
    return jsonify(stored_data) 