# -*- coding: utf-8 -*-
"""
Player substitution management.

Handles mid-tournament player substitutions and table count reductions,
including updating seating arrangements and player assignments while
maintaining optimal seating patterns.
"""

import importlib

from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
    session,
    Response,
    stream_with_context,
)
from flask_login import current_user

from oauth_setup import (
    admin_or_editor_required,
    logging,
    login_required,
    MIN_TABLES,
    tournament_required,
)
from write_sheet import googlesheet

blueprint = Blueprint("sub", __name__, url_prefix="/sub")


@blueprint.route("/player_substitution")
@admin_or_editor_required
@tournament_required
@login_required
def player_substitution():
    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)

    batch_data = googlesheet.batch_get_tournament_data(sheet)
    completed_rounds = googlesheet.count_completed_hanchan_from_batch(batch_data)

    # Get players data
    raw_players = googlesheet.get_players_from_batch(batch_data)
    players = []

    # Initialize counters
    players_with_seating = 0
    subs_with_seating = 0
    subs_without_seating = 0

    for p in raw_players:
        has_seating = p[0] != ""
        # Get status from column D (index 3), fallback to old logic if not present
        status = (
            p[3]
            if len(p) > 3 and p[3]
            else (
                "active"
                if has_seating
                else ("substitute" if "sub" in str(p[1]).lower() else "substitute")
            )
        )
        is_sub = (
            "sub" in str(p[1]).lower()
        )  # Check registration ID for "sub" (for backward compatibility)

        # Update counters based on new status system
        if status == "active" and has_seating:
            players_with_seating += 1
        elif status == "substitute" and has_seating:
            subs_with_seating += 1
        elif status == "substitute" and not has_seating:
            subs_without_seating += 1

        player = {
            "registration_id": str(p[1]),
            "seating_id": p[0] if has_seating else None,
            "name": p[2] if len(p) > 2 else f"player {p[1]}",
            "status": status,
            "is_current": status == "active",
            "substituted_for": p[4] if len(p) > 4 else "",
        }
        players.append(player)

    # Get current seating arrangement
    seatlist = googlesheet.get_seating_from_batch(batch_data)
    seating = seatlist_to_seating(seatlist)

    # Count total dropouts for table reduction logic
    total_dropouts = googlesheet.count_total_dropouts(sheet)

    return render_template(
        "player_substitution.html",
        completed_rounds=completed_rounds,
        min_tables=MIN_TABLES,
        players=players,
        players_with_seating=players_with_seating,
        seating=seating,
        subs_with_seating=subs_with_seating,
        subs_without_seating=subs_without_seating,
        total_dropouts=total_dropouts,
    )


@blueprint.route("/confirm_substitutions", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def confirm_substitutions():
    new_seating = session.pop("new_seating", None)
    if not new_seating:
        return jsonify({"status": "error", "message": "No substitution data found"})

    # Get the reduce table count preference and dropped players from the request
    data = request.json or {}
    reduce_table_count = data.get("reduceTableCount", False)
    dropped_players = data.get("droppedPlayers", [])
    automatic_table_reduction = data.get("automaticTableReduction", False)
    substitutes_to_deactivate = data.get("substitutesToDeactivate", [])

    logging.info(f"=== SUBSTITUTION REQUEST ===")
    logging.info(f"Request data: {data}")
    logging.info(f"Reduce table count: {reduce_table_count}")
    logging.info(f"Dropped players: {dropped_players}")
    logging.info(f"Automatic table reduction: {automatic_table_reduction}")
    logging.info(f"Substitutes to deactivate: {substitutes_to_deactivate}")

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    seatlist = seating_to_seatlist(new_seating)
    # Get current seating for backup using batch
    batch_data = googlesheet.batch_get_tournament_data(sheet)
    session["last_seating"] = googlesheet.get_seating_from_batch(batch_data)

    logging.info(f"New seating seatlist (first 3 rows): {seatlist[:3]}")
    logging.info(f"Old seating (from session, first 3 rows): {session['last_seating'][:3]}")

    # Get old seating IDs for comparison
    old_seatlist = session["last_seating"]
    old_active_ids = {player for row in old_seatlist for player in row[2:6] if player}
    new_active_ids = {player for row in seatlist for player in row[2:6] if player}

    logging.info(f"Old active seating IDs: {sorted(old_active_ids)}")
    logging.info(f"New active seating IDs: {sorted(new_active_ids)}")

    # Update player statuses for dropped players BEFORE updating seating
    if dropped_players:
        logging.info(f"Marking players as dropped: {dropped_players}")
        googlesheet.remove_players(sheet, dropped_players)

    # Handle automatic table reduction by deactivating selected substitutes
    if automatic_table_reduction and substitutes_to_deactivate:
        logging.info(f"=== AUTOMATIC TABLE REDUCTION ===")
        seating_ids_to_deactivate = [sub["seating_id"] for sub in substitutes_to_deactivate]
        logging.info(f"Deactivating substitutes with seating IDs: {seating_ids_to_deactivate}")
        
        # Sort by descending seating ID for logging consistency
        seating_ids_to_deactivate.sort(reverse=True)
        
        try:
            googlesheet.update_substitute_to_regular_status(sheet, seating_ids_to_deactivate)
            logging.info(f"Successfully deactivated {len(seating_ids_to_deactivate)} substitutes")
        except Exception as e:
            logging.error(f"Error deactivating substitutes: {str(e)}")
            return jsonify({"status": "error", "message": f"Failed to deactivate substitutes: {str(e)}"})
    elif automatic_table_reduction:
        logging.info("Automatic table reduction requested but no substitutes to deactivate")
    
    # Force table reduction when automatic table reduction is active
    if automatic_table_reduction:
        reduce_table_count = True
        logging.info("Forcing table count reduction due to automatic table reduction")

    # Re-fetch player data after removing players to get current state
    fresh_batch_data = googlesheet.batch_get_tournament_data(sheet)
    raw_players = googlesheet.get_players_from_batch(fresh_batch_data)
    
    logging.info(f"Player data after marking dropouts:")
    for i, p in enumerate(raw_players[:10]):  # Log first 10 players
        status = p[3] if len(p) > 3 and p[3] else "no_status"
        logging.info(f"  Player {i+1}: seating_id={p[0]}, reg_id={p[1]}, name={p[2] if len(p) > 2 else 'no_name'}, status={status}")

    # Identify new seating IDs that were created for substitutes
    max_old_id = max(old_active_ids) if old_active_ids else 0
    new_substitute_ids = [sid for sid in new_active_ids if sid > max_old_id]
    new_substitute_ids.sort()  # Ensure consistent ordering

    logging.info(f"Max old seating ID: {max_old_id}")
    logging.info(f"New substitute seating IDs needed: {new_substitute_ids}")

    # Get all substitute players (all with status="substitute" are available)
    all_substitutes = []
    for p in raw_players:
        has_seating = p[0] != ""
        status = p[3] if len(p) > 3 and p[3] else ""
        if status == "substitute":
            all_substitutes.append({
                'registration_id': str(p[1]),
                'seating_id': int(p[0]) if has_seating else None,
                'name': p[2] if len(p) > 2 else f"player {p[1]}"
            })

    # Sort substitutes for consistent assignment order  
    all_substitutes.sort(key=lambda x: x['registration_id'])

    logging.info(f"All substitute players found (all available):")
    for sub in all_substitutes:
        logging.info(f"  {sub['name']} (reg_id: {sub['registration_id']}, seating_id: {sub['seating_id']})")
    
    # Check if we have enough substitutes for the number needed
    substitutes_needed = len(new_substitute_ids)
    substitutes_available = len(all_substitutes)
    
    logging.info(f"Optimizer generated substitute seating IDs: {new_substitute_ids}")
    logging.info(f"Substitutes needed: {substitutes_needed}")
    logging.info(f"Substitutes available: {substitutes_available}")
    
    if substitutes_available < substitutes_needed:
        logging.warning(f"INSUFFICIENT SUBSTITUTES: Need {substitutes_needed} but only have {substitutes_available} available!")
        logging.warning(f"Will proceed with partial substitution using {substitutes_available} substitutes")
        # Continue processing with available substitutes rather than failing completely
    
    # Create mapping from optimizer's substitute IDs to actual substitute seating IDs
    # Strategy: Use existing substitute seating IDs where possible, assign new ones as needed
    id_mapping = {}
    actual_substitute_ids = []
    
    # First, collect existing substitute seating IDs
    existing_substitute_ids = [sub['seating_id'] for sub in all_substitutes if sub['seating_id'] is not None]
    existing_substitute_ids.sort()
    
    # Then, determine what new seating IDs we need for substitutes without IDs
    unassigned_substitutes = [sub for sub in all_substitutes if sub['seating_id'] is None]
    
    if existing_substitute_ids:
        actual_substitute_ids.extend(existing_substitute_ids)
        logging.info(f"Using existing substitute seating IDs: {existing_substitute_ids}")
    
    if unassigned_substitutes:
        # Find the next available seating IDs for unassigned substitutes
        all_used_ids = old_active_ids.copy()
        if existing_substitute_ids:
            all_used_ids.update(existing_substitute_ids)
        
        next_seating_id = max(all_used_ids) + 1 if all_used_ids else 1
        new_ids = list(range(next_seating_id, next_seating_id + len(unassigned_substitutes)))
        actual_substitute_ids.extend(new_ids)
        logging.info(f"Assigning new seating IDs {new_ids} to unassigned substitutes")
        
        # Create assignments for unassigned substitutes
        substitute_assignments = {}
        for i, sub in enumerate(unassigned_substitutes):
            substitute_assignments[sub['registration_id']] = new_ids[i]
            logging.info(f"Assigning seating ID {new_ids[i]} to {sub['name']} (reg_id: {sub['registration_id']})")
        
        # Apply substitute assignments
        if substitute_assignments:
            logging.info(f"Calling add_substitute_players with: {substitute_assignments}")
            googlesheet.add_substitute_players(sheet, substitute_assignments)
    
    # Create mapping from optimizer IDs to actual substitute IDs
    actual_substitute_ids.sort()
    
    # Only map as many substitutes as we actually have available
    max_mappings = min(len(new_substitute_ids), len(actual_substitute_ids))
    
    for i in range(max_mappings):
        optimizer_id = new_substitute_ids[i]
        actual_id = actual_substitute_ids[i]
        id_mapping[optimizer_id] = actual_id
        logging.info(f"Mapping optimizer substitute ID {optimizer_id} -> actual substitute ID {actual_id}")
    
    # Log any unmapped optimizer IDs (indicates insufficient substitutes)
    unmapped_optimizer_ids = new_substitute_ids[max_mappings:] if max_mappings < len(new_substitute_ids) else []
    if unmapped_optimizer_ids:
        logging.warning(f"Unable to map optimizer substitute IDs {unmapped_optimizer_ids} - insufficient substitute players!")
    
    # Apply the ID mapping to the seating arrangement
    if id_mapping or unmapped_optimizer_ids:
        logging.info(f"Applying ID mapping to seating: {id_mapping}")
        for round_idx in range(len(new_seating)):
            for table_idx in range(len(new_seating[round_idx])):
                for seat_idx in range(4):
                    seat_id = new_seating[round_idx][table_idx][seat_idx]
                    if seat_id in id_mapping:
                        new_seating[round_idx][table_idx][seat_idx] = id_mapping[seat_id]
                        logging.info(f"  Round {round_idx+1}, Table {table_idx+1}, Seat {seat_idx+1}: {seat_id} -> {id_mapping[seat_id]}")
                    elif seat_id in unmapped_optimizer_ids:
                        # Set unmapped substitute positions to empty (0) since we don't have substitutes for them
                        new_seating[round_idx][table_idx][seat_idx] = 0
                        logging.warning(f"  Round {round_idx+1}, Table {table_idx+1}, Seat {seat_idx+1}: {seat_id} -> 0 (no substitute available)")
        
        # Update the seatlist to reflect the corrected seating arrangement
        seatlist = seating_to_seatlist(new_seating)
        
        # Store the corrected seating in session for future reference
        session["new_seating"] = new_seating
        
        logging.info(f"=== SEATING CORRECTION COMPLETE ===")
        logging.info(f"Successfully mapped {len(id_mapping)} substitute IDs")
        if unmapped_optimizer_ids:
            logging.info(f"Failed to map {len(unmapped_optimizer_ids)} substitute IDs due to insufficient substitutes")

    # Update remaining player statuses to match the final seating arrangement
    # Get the set of all seating IDs that appear in the new seating
    active_seating_ids = {player for row in seatlist for player in row[2:6] if player}

    # Re-fetch player data after substitute assignments
    final_batch_data = googlesheet.batch_get_tournament_data(sheet)
    final_raw_players = googlesheet.get_players_from_batch(final_batch_data)
    players_sheet = googlesheet.get_sheet(tournament.google_doc_id).worksheet("players")
    status_updates = []

    logging.info(f"Final player status check - active seating IDs: {sorted(active_seating_ids)}")
    
    for row_idx, p in enumerate(final_raw_players, start=4):
        current_seating_id = p[0] if p[0] else None
        registration_id = str(p[1])
        current_status = p[3] if len(p) > 3 and p[3] else ""

        # Determine what the status should be based on the new seating
        if current_seating_id and int(current_seating_id) in active_seating_ids:
            # Player has a seating ID and appears in new seating - should be active
            if current_status != "active":
                logging.info(f"  Player {registration_id} (seat {current_seating_id}): {current_status} -> active")
                status_updates.append({"range": f"D{row_idx}", "values": [["active"]]})
        elif current_status == "active":
            # Player was active but is no longer in seating - should be dropped
            # (This handles cases where the dropped_players list might miss someone)
            logging.info(f"  Player {registration_id} (seat {current_seating_id}): active -> dropped (not in new seating)")
            status_updates.append({"range": f"D{row_idx}", "values": [["dropped"]]})

    logging.info(f"Final status updates to apply: {status_updates}")
    if status_updates:
        players_sheet.batch_update(status_updates)

    # Track substitutions by analyzing seating changes
    old_seating = seatlist_to_seating(old_seatlist)

    # Track automatic substitutions before updating seating
    googlesheet.track_substitutions(sheet, old_seating, new_seating, dropped_players)

    # If reducing table count, identify substitutes who are no longer playing
    if reduce_table_count:
        # Find players who were in the old seating but not in the new seating
        no_longer_playing = old_active_ids - new_active_ids

        if no_longer_playing:
            # Clear substitution tracking for players no longer playing
            googlesheet.clear_substitution_tracking(sheet, list(no_longer_playing))

    # Pass the reduce_table_count parameter to update_seating
    googlesheet.update_seating(sheet, seatlist, reduce_table_count)
    from .run import update_scores

    update_scores()
    return jsonify({"status": "success"})


@blueprint.route("/undo_substitution", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def undo_substitution():
    last_seating = session.pop("last_seating", None)
    if not last_seating:
        return jsonify({"status": "error", "message": "No previous seating found"})

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)

    googlesheet.update_seating(sheet, last_seating)

    return jsonify({"status": "success"})


def seatlist_to_seating(seatlist):
    hanchan_count = max([p[0] for p in seatlist])
    table_count = max([p[1] for p in seatlist])
    seating = [[[] for _ in range(table_count)] for _ in range(hanchan_count)]
    for p in seatlist:
        seating[p[0] - 1][p[1] - 1] = p[2:]
    return seating


def seating_to_seatlist(seating):
    return [
        (
            h + 1,
            t + 1,
            seating[h][t][0],
            seating[h][t][1],
            seating[h][t][2],
            seating[h][t][3],
        )
        for h in range(len(seating))
        for t in range(len(seating[h]))
    ]


@blueprint.route("/store_seating", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def store_seating():
    data = request.json
    if not data or "seating" not in data:
        return jsonify({"status": "error", "message": "No seating data provided"}), 400

    session["new_seating"] = data["seating"]
    return jsonify({"status": "success"})


@blueprint.route("/analyze_seating", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def analyze_seating():
    data = request.json
    if not data or "seating" not in data:
        return jsonify({"status": "error", "message": "No seating data provided"}), 400

    from seating.gams.make_stats import make_stats

    # Get current seating for comparison
    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    batch_data = googlesheet.batch_get_tournament_data(sheet)
    current_seatlist = googlesheet.get_seating_from_batch(batch_data)
    current_seating = seatlist_to_seating(current_seatlist)

    # Find the highest player ID in the current seating
    max_id = max(
        max(player for table in round for player in table) for round in current_seating
    )

    # Calculate stats for both seating arrangements
    # For current seating, only ignore empty seats (0)
    current_stats = make_stats(current_seating, ignore_players=[0])

    # For new seating, identify which rounds changed and which players are in those rounds
    # First, identify which rounds have changed by comparing current vs new seating
    changed_rounds = []
    for round_idx in range(len(data["seating"])):
        if (
            round_idx < len(current_seating)
            and data["seating"][round_idx] != current_seating[round_idx]
        ):
            changed_rounds.append(round_idx)

    # Find all players who appear in the changed rounds
    players_in_changed_rounds = set()
    for round_idx in changed_rounds:
        for table in data["seating"][round_idx]:
            for player in table:
                if player != 0:
                    players_in_changed_rounds.add(player)

    # For statistics, we want to consider only the players who appear in changed rounds
    # All other players should be ignored, including any players who might have higher IDs
    # but don't participate in the changed rounds
    all_players_in_new_seating = set()
    for round in data["seating"]:
        for table in round:
            for player in table:
                if player != 0:
                    all_players_in_new_seating.add(player)

    # Find the maximum player ID to determine the full range of possible players
    max_player_id_in_new = (
        max(all_players_in_new_seating) if all_players_in_new_seating else 0
    )

    # Ignore all players who are not in the changed rounds
    # This includes both players who appear in unchanged rounds and players who don't appear at all
    all_possible_players = set(range(1, max_player_id_in_new + 1))
    players_to_ignore = [0] + list(all_possible_players - players_in_changed_rounds)
    new_stats = make_stats(data["seating"], ignore_players=players_to_ignore)
    return jsonify({"status": "success", "current": current_stats, "new": new_stats})


@blueprint.route("/check_table_reduction", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def check_table_reduction():
    """Check if automatic table reduction is required."""
    data = request.json or {}
    current_players = data.get("currentPlayers", [])
    available_substitutes = data.get("availableSubstitutes", [])
    
    if not current_players:
        return jsonify({"status": "error", "message": "No current players data provided"}), 400

    # Get active substitutes (players with substituted_for field)
    active_substitutes = [p for p in current_players if p.get("substituted_for")]
    current_active_count = len(current_players)
    
    # Calculate players needed to fill to next multiple of 4
    players_needed_for_next_table = (4 - (current_active_count % 4)) % 4
    
    # Check if automatic table reduction is required
    must_reduce_tables = players_needed_for_next_table > len(available_substitutes) and len(active_substitutes) > 0
    
    if must_reduce_tables:
        # Calculate target player count (largest multiple of 4 <= current count)
        target_player_count = (current_active_count // 4) * 4
        substitutes_to_deactivate_count = current_active_count - target_player_count
        
        # Sort active substitutes by seating ID (descending) for priority deactivation
        sorted_active_substitutes = sorted(
            [s for s in active_substitutes if s.get("seating_id")],
            key=lambda x: int(x["seating_id"]),
            reverse=True
        )
        
        recommended_substitutes = sorted_active_substitutes[:substitutes_to_deactivate_count]
        
        return jsonify({
            "status": "success",
            "automaticReductionRequired": True,
            "currentActiveCount": current_active_count,
            "targetPlayerCount": target_player_count,
            "availableSubstitutes": len(available_substitutes),
            "playersNeededForNextTable": players_needed_for_next_table,
            "recommendedSubstitutes": recommended_substitutes
        })
    
    return jsonify({
        "status": "success",
        "automaticReductionRequired": False
    })


@blueprint.route("/deactivate_substitutes", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def deactivate_substitutes():
    """Deactivate selected substitutes for automatic table reduction."""
    data = request.json
    if not data or "substitutesToDeactivate" not in data:
        return jsonify({"status": "error", "message": "No substitutes data provided"}), 400

    substitutes_to_deactivate = data["substitutesToDeactivate"]
    if not substitutes_to_deactivate:
        return jsonify({"status": "error", "message": "No substitutes selected for deactivation"}), 400

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    
    try:
        # Convert to seating IDs for the googlesheet function
        seating_ids = [sub["seating_id"] for sub in substitutes_to_deactivate]
        
        logging.info(f"Deactivating substitutes with seating IDs: {seating_ids}")
        
        # Use existing function to update substitute status
        googlesheet.update_substitute_to_regular_status(sheet, seating_ids)
        
        return jsonify({"status": "success", "message": f"Deactivated {len(seating_ids)} substitutes"})
        
    except Exception as e:
        logging.error(f"Error deactivating substitutes: {str(e)}")
        return jsonify({"status": "error", "message": f"Failed to deactivate substitutes: {str(e)}"}), 500


@blueprint.route("/get_predefined_seating", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def get_predefined_seating():
    """Get predefined seating template for the specified table count."""
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    table_count = data.get("tableCount")
    completed_rounds = data.get("completedRounds", 0)

    if not table_count:
        return jsonify({"status": "error", "message": "No table count specified"}), 400

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)

    # Get total number of rounds in the tournament
    batch_data = googlesheet.batch_get_tournament_data(sheet)
    schedule = googlesheet.get_schedule_from_batch(batch_data)
    total_rounds = len(schedule["rounds"])

    try:
        # Try to import the seating module
        seating_module = importlib.import_module(f"seating.seats_{total_rounds}")
        player_count = table_count * 4

        if player_count not in seating_module.seats:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"No predefined seating for {player_count} players",
                    }
                ),
                404,
            )

        # Get the predefined seating plan
        predefined_seating = seating_module.seats[player_count]

        # Convert to the seating format expected by the frontend
        seating = [[[] for _ in range(table_count)] for _ in range(total_rounds)]
        for round_idx in range(total_rounds):
            for table_idx in range(table_count):
                if round_idx < len(predefined_seating) and table_idx < len(
                    predefined_seating[round_idx]
                ):
                    seating[round_idx][table_idx] = predefined_seating[round_idx][
                        table_idx
                    ]
                else:
                    # Fill with zeros if table doesn't exist in the seating plan
                    seating[round_idx][table_idx] = [0, 0, 0, 0]

        return jsonify({"status": "success", "seating": seating})

    except (ImportError, KeyError, AttributeError) as e:
        logging.error(f"Error fetching predefined seating: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to get predefined seating: {str(e)}",
                }
            ),
            500,
        )
