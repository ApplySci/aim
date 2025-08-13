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

    # Get players data with statuses
    parsed_players = googlesheet.list_players(sheet)
    players = []

    # Initialize counters
    players_with_seating = 0
    subs_with_seating = 0
    subs_without_seating = 0

    for p in parsed_players:
        is_current = p["status"] == "playing"
        if is_current:
            players_with_seating += 1
            if p.get("is_sub"):
                subs_with_seating += 1
        else:
            if p["status"] == "sub_waiting":
                subs_without_seating += 1

        players.append(
            {
                "registration_id": str(p["registration_id"]),
                "seating_id": p.get("seating_id"),
                "name": p.get("name"),
                "is_current": is_current,
                "status": p.get("status"),
                "replaces_registration_id": p.get("replaces_registration_id"),
                "original_status": p.get("status"),
            }
        )

    # Get current seating arrangement
    seatlist = googlesheet.get_seating_from_batch(batch_data)
    seating = seatlist_to_seating(seatlist)

    return render_template(
        "player_substitution.html",
        completed_rounds=completed_rounds,
        min_tables=MIN_TABLES,
        players=players,
        players_with_seating=players_with_seating,
        seating=seating,
        subs_with_seating=subs_with_seating,
        subs_without_seating=subs_without_seating,
    )


@blueprint.route("/plan_substitutions", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def plan_substitutions():
    data = request.json or {}
    removed_regs = data.get("removed", [])
    returning_regs = data.get("returning", [])

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)

    logging.debug(f"Plan substitutions: removed={removed_regs}, returning={returning_regs}")

    batch_data = googlesheet.batch_get_tournament_data(sheet)
    completed_rounds = googlesheet.count_completed_hanchan_from_batch(batch_data)
    schedule = googlesheet.get_schedule_from_batch(batch_data)
    total_rounds = len(schedule["rounds"]) if schedule else 0

    players = googlesheet.list_players(sheet)
    reg_to_player = {p["registration_id"]: dict(p) for p in players}

    # Capture current max seating id
    current_ids = [p["seating_id"] for p in players if p.get("seating_id")]
    max_id = max(current_ids) if current_ids else 0

    # Work on a copy state
    changes = {}
    messages = []

    def set_state(reg, status=None, seating_id=None, replaces=None):
        pl = reg_to_player.get(reg)
        if not pl:
            return
        if status is not None:
            pl["status"] = status
        if seating_id is not None or seating_id == None:
            pl["seating_id"] = seating_id
        if replaces is not None or replaces == None:
            pl["replaces_registration_id"] = replaces
        changes[reg] = {
            "registration_id": reg,
            "status": pl["status"],
            "seating_id": pl.get("seating_id"),
            "replaces_registration_id": pl.get("replaces_registration_id") or "",
        }

    # 1) Swap back returns where a playing sub is currently covering them
    for reg in returning_regs:
        pl = reg_to_player.get(reg)
        if not pl:
            continue
        # Find playing sub that replaced this reg
        covering_sub = None
        for sp in players:
            if (
                sp.get("status") == "playing"
                and sp.get("replaces_registration_id") == reg
                and sp.get("is_sub")
            ):
                covering_sub = sp
                break
        if covering_sub:
            seat = covering_sub.get("seating_id")
            logging.debug(
                f"Swap-back: returnee {reg} takes seat {seat}, sub {covering_sub['registration_id']} back to waiting"
            )
            # Demote sub
            set_state(covering_sub["registration_id"], status="sub_waiting", seating_id=None, replaces=None)
            # Promote returnee into that seat
            set_state(reg, status="playing", seating_id=seat, replaces=None)
            messages.append(f"Returnee {reg} swapped back into seat {seat}")

    # 2) Remove selected players
    freed_seats: list[tuple[int, str]] = []  # (seat_id, removed_reg)
    for reg in removed_regs:
        pl = reg_to_player.get(reg)
        if pl and pl.get("status") == "playing" and pl.get("seating_id"):
            seat = pl["seating_id"]
            set_state(reg, status="removed", seating_id=None, replaces=None)
            freed_seats.append((seat, reg))
            logging.debug(f"Removing playing player {reg} from seat {seat}")

    # Recompute waiting subs list
    waiting_subs = [p for p in reg_to_player.values() if p.get("status") == "sub_waiting"]
    waiting_subs.sort(key=lambda x: x.get("registration_id"))

    # Assign waiting subs into freed seats in order
    assigned_subs = []
    for seat, removed_reg in freed_seats:
        if waiting_subs:
            sub = waiting_subs.pop(0)
            set_state(
                sub["registration_id"],
                status="playing",
                seating_id=seat,
                replaces=removed_reg,
            )
            assigned_subs.append(sub["registration_id"])
            logging.debug(f"Assign sub {sub['registration_id']} to freed seat {seat} (replaces {removed_reg})")

    holes = len(freed_seats) - len(assigned_subs)
    if holes > 0:
        messages.append(f"{holes} holes remain after assigning all waiting subs")
        logging.debug(f"Holes remaining: {holes}")

    # 3) Handle remaining returns using playing subs if any are left
    pending_returns = [r for r in returning_regs if reg_to_player.get(r, {}).get("status") != "playing"]
    # Identify playing subs not covering a specific returnee (after swap-back and assignments)
    playing_subs = [p for p in reg_to_player.values() if p.get("status") == "playing" and p.get("is_sub")]
    for reg in pending_returns[:]:
        if playing_subs:
            sub = playing_subs.pop(0)
            seat = sub.get("seating_id")
            set_state(sub["registration_id"], status="sub_waiting", seating_id=None, replaces=None)
            set_state(reg, status="playing", seating_id=seat, replaces=None)
            messages.append(f"Returnee {reg} replaces playing sub at seat {seat}")
            logging.debug(f"Returnee {reg} replaces playing sub {sub['registration_id']} at seat {seat}")
            pending_returns.remove(reg)

    # 4) Compute active players and divisibility; demote extra playing subs if needed
    def count_active():
        return len([p for p in reg_to_player.values() if p.get("status") == "playing"])

    active_players = count_active()
    demoted_for_divisibility = []
    if active_players % 4 != 0:
        # Demote some playing subs to reach multiple of 4
        need = active_players % 4
        subs_playing = [p for p in reg_to_player.values() if p.get("status") == "playing" and p.get("is_sub")]
        subs_playing.sort(key=lambda x: x.get("seating_id") or 0, reverse=True)
        for i in range(need):
            if i < len(subs_playing):
                sp = subs_playing[i]
                set_state(sp["registration_id"], status="sub_waiting", seating_id=None, replaces=None)
                demoted_for_divisibility.append(sp["registration_id"])
                logging.debug(f"Demoting playing sub {sp['registration_id']} to fix divisibility")
        active_players = count_active()

    # 5) Handle any remaining returns. Only increase tables if cannot demote any more subs and can add full tables.
    substitutes_ids_to_add: list[int] = []
    if pending_returns:
        # No more playing subs to demote at this point.
        can_add = 4 - (active_players % 4) if (active_players % 4) != 0 else 0
        to_add = 0
        if active_players % 4 == 0:
            # We can add in groups of 4 only
            to_add = (len(pending_returns) // 4) * 4
        else:
            # We can add up to 'can_add' to reach next multiple of 4
            to_add = min(len(pending_returns), can_add)
        if to_add > 0:
            for i in range(to_add):
                reg = pending_returns[i]
                max_id += 1
                new_id = max_id
                set_state(reg, status="playing", seating_id=new_id, replaces=None)
                substitutes_ids_to_add.append(new_id)
                logging.debug(f"Adding returnee {reg} with new seat id {new_id}")
            messages.append(f"Added {to_add} returning players; tables may increase if needed")
        else:
            if pending_returns:
                messages.append(
                    f"Deferred {len(pending_returns)} returning players (not enough to form full tables without removing more subs)"
                )
                logging.debug(
                    f"Deferred returns: {pending_returns} (cannot increase tables under constraints)"
                )

    # Final counts and table plan
    active_players = count_active()
    new_table_count = active_players // 4
    old_table_count = (len(current_ids) // 4) if current_ids else 0

    # Decide strategy
    from oauth_setup import MIN_TABLES as MIN_T
    if completed_rounds == 0:
        if new_table_count >= MIN_T:
            strategy = "prearranged"
        else:
            strategy = "prearranged_then_optimize"
    else:
        strategy = "optimize" if new_table_count != old_table_count else "optimize_if_needed"

    # Build omitPlayers as seat ids that were previously active but are no longer active after the plan
    current_active_ids_set = set([sid for sid in current_ids])
    new_active_ids_set = set(
        [
            p.get("seating_id")
            for p in reg_to_player.values()
            if p.get("status") == "playing" and p.get("seating_id") is not None
        ]
    )
    omit_players = [int(x) for x in current_active_ids_set - new_active_ids_set]

    logging.debug(
        f"Plan result: active={active_players}, new_tables={new_table_count}, strategy={strategy}, omit={omit_players}, add={substitutes_ids_to_add}"
    )

    # Persist plan into session for confirm
    session["plan_changes"] = list(changes.values())
    session["plan_info"] = {
        "omitPlayers": omit_players,
        "substitutes": substitutes_ids_to_add,
        "newTableCount": new_table_count,
        "strategy": strategy,
        "messages": messages,
        "completedRounds": completed_rounds,
        "totalRounds": total_rounds,
    }

    return jsonify(
        {
            "status": "success",
            "omitPlayers": omit_players,
            "substitutes": substitutes_ids_to_add,
            "newTableCount": new_table_count,
            "strategy": strategy,
            "messages": messages,
        }
    )


@blueprint.route("/confirm_substitutions", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def confirm_substitutions():
    new_seating = session.get("new_seating")
    plan_changes = session.get("plan_changes")
    plan_info = session.get("plan_info")
    if not new_seating or not plan_changes or not plan_info:
        return jsonify({"status": "error", "message": "Missing planned substitution data"})

    # Get the reduce table count preference from the request
    data = request.json or {}
    reduce_table_count = data.get("reduceTableCount", False)

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)

    # Get current seating for backup using batch
    batch_data = googlesheet.batch_get_tournament_data(sheet)
    session["last_seating"] = googlesheet.get_seating_from_batch(batch_data)

    # Snapshot player columns for undo
    try:
        session["last_player_snapshot"] = googlesheet.snapshot_player_columns(sheet)
    except Exception as e:
        logging.error(f"Failed to snapshot player columns: {str(e)}")

    # Apply minimal renumbering for prearranged strategies at round 0
    try:
        if plan_info.get("completedRounds", 0) == 0 and plan_info.get("strategy") in (
            "prearranged",
            "prearranged_then_optimize",
        ):
            # Determine target M from seating
            target_ids = set()
            for rnd in new_seating:
                for tbl in rnd:
                    for pid in tbl:
                        if pid:
                            target_ids.add(int(pid))
            if target_ids:
                max_target = max(target_ids)
                # Build map from current active ids to constrained 1..M keeping as many as possible
                # Gather playing players from plan_changes
                playing_regs = [c["registration_id"] for c in plan_changes if c.get("status") == "playing"]
                # Build dict reg->current id from changes
                reg_to_id = {c["registration_id"]: c.get("seating_id") for c in plan_changes}
                current_active_ids = [reg_to_id.get(r) for r in playing_regs if reg_to_id.get(r)]
                keep = [pid for pid in current_active_ids if 1 <= int(pid) <= max_target]
                keep_set = set(int(x) for x in keep)
                free = [x for x in range(1, max_target + 1) if x not in keep_set]
                # Map any ids not in 1..M to smallest free
                remap = {}
                for pid in current_active_ids:
                    if int(pid) not in keep_set:
                        if free:
                            new_id = free.pop(0)
                            remap[int(pid)] = new_id
                if remap:
                    logging.debug(f"Applying minimal renumber map: {remap}")
                    # Update plan_changes seating_id according to remap
                    for ch in plan_changes:
                        sid = ch.get("seating_id")
                        if sid and int(sid) in remap:
                            ch["seating_id"] = remap[int(sid)]
    except Exception as e:
        logging.error(f"Minimal renumbering failed: {str(e)}", exc_info=True)

    # Apply player changes
    try:
        googlesheet.batch_apply_player_changes(sheet, plan_changes)
        logging.debug(f"Applied player changes: {plan_changes}")
    except Exception as e:
        logging.error(f"Failed to apply player changes: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to write player updates"})

    # Write seating
    try:
        seatlist = seating_to_seatlist(new_seating)
        # If we had holes earlier or strategy implies reduction, enforce reduce_table_count
        auto_reduce = plan_info.get("strategy") in ("prearranged_then_optimize", "optimize") and True
        googlesheet.update_seating(sheet, seatlist, reduce_table_count or auto_reduce)
        logging.debug(
            f"Updated seating with reduce_table_count={reduce_table_count or auto_reduce}"
        )
    except Exception as e:
        logging.error(f"Failed to update seating: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to update seating"})

    # Clear planning session after successful apply
    session.pop("plan_changes", None)
    session.pop("plan_info", None)
    session.pop("new_seating", None)

    from .run import update_scores

    update_scores()
    return jsonify({"status": "success"})


@blueprint.route("/undo_substitution", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def undo_substitution():
    last_seating = session.pop("last_seating", None)
    last_player_snapshot = session.pop("last_player_snapshot", None)
    if not last_seating:
        return jsonify({"status": "error", "message": "No previous seating found"})

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)

    try:
        googlesheet.update_seating(sheet, last_seating)
        logging.debug("Restored previous seating")
        if last_player_snapshot:
            googlesheet.restore_player_columns(sheet, last_player_snapshot)
            logging.debug("Restored previous player status columns")
    except Exception as e:
        logging.error(f"Undo failed: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to undo substitution"})

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
