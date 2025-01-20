# -*- coding: utf-8 -*-
"""
User management and access control.

Handles user roles and permissions for tournaments, including adding users,
modifying access levels, and synchronizing permissions between the local
database and Google Sheets.
"""

from flask import Blueprint, redirect, url_for, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from models import Access, User, Tournament
from oauth_setup import (
    admin_required,
    admin_or_editor_required,
    db,
    login_required,
    logging,
    Role,
    superadmin_required,
)
from forms.userform import AddUserForm
from write_sheet import googlesheet

blueprint = Blueprint("user_management", __name__)


@blueprint.route("/run/add_user", methods=["POST"])
@admin_or_editor_required
@login_required
def add_user_post():
    if not current_user.live_tournament_id:
        flash("Please select a tournament first.", "warning")
        return redirect(url_for("run.select_tournament"))

    form = AddUserForm()

    if not form.validate_on_submit():
        return add_user_get()

    email = form.email.data.lower()
    role = form.role.data

    # Ensure the user record exists
    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    # Add the user to the tournament with the specified role
    access = (
        db.session.query(Access)
        .filter_by(user_email=email, tournament_id=current_user.live_tournament_id)
        .first()
    )
    if not access:
        tournament = db.session.query(Tournament).get(current_user.live_tournament_id)
        access = Access(email, tournament=tournament, role=Role[role])
        db.session.add(access)
        db.session.commit()
        share_result = googlesheet.share_sheet(
            tournament.google_doc_id, email, notify=False
        )
        if share_result == True:
            flash("User added successfully!", "success")
        else:
            flash(f"Failed to add user: {share_result}", "danger")
    else:
        flash("User is already attached to this tournament.", "info")

    return redirect(url_for("user_management.add_user_get"))


@blueprint.route("/run/add_user", methods=["GET"])
@admin_or_editor_required
@login_required
def add_user_get():
    if not current_user.live_tournament_id:
        flash("Please select a tournament first.", "warning")
        return redirect(url_for("run.select_tournament"))

    form = AddUserForm()

    tournament = db.session.query(Tournament).get(current_user.live_tournament_id)

    # Fetch users for the current tournament from the database
    db_users = (
        db.session.query(User, Access.role)
        .join(Access)
        .filter(Access.tournament_id == current_user.live_tournament_id)
        .all()
    )

    # Get users who have access to the Google Sheet
    sheet_users = googlesheet.get_sheet_users(tournament.google_doc_id)

    if isinstance(sheet_users, str):  # Error occurred
        flash(f"Error checking Google Sheet access: {sheet_users}", "danger")
        sheet_users = []

    # Check if the current user is an admin for this tournament
    is_admin = current_user.live_tournament_role == Role.admin

    # Filter out service account emails
    def is_valid_user_email(email):
        return not (
            email.startswith("firebase-adminsdk")
            or email.endswith("gserviceaccount.com")
        )

    # Prepare user lists
    db_user_emails = {
        user.email for user, _ in db_users if is_valid_user_email(user.email)
    }
    sheet_user_emails = {
        user["email"] for user in sheet_users if is_valid_user_email(user["email"])
    }

    missing_from_sheet = db_user_emails - sheet_user_emails
    missing_from_db = sheet_user_emails - db_user_emails

    # Convert to list of dictionaries and sort
    users = [
        {
            "email": user.email,
            "role": role.value,
            "in_sheet": user.email in sheet_user_emails,
        }
        for user, role in db_users
        if is_valid_user_email(user.email)
    ]

    # Add users who are in the sheet but not in the database
    users.extend(
        [
            {"email": email, "role": "Unknown", "in_sheet": True, "in_db": False}
            for email in missing_from_db
            if is_valid_user_email(email)
        ]
    )

    # Separate current user and sort others
    current_user_data = next(
        (user for user in users if user["email"] == current_user.email), None
    )
    other_users = [user for user in users if user["email"] != current_user.email]
    other_users.sort(key=lambda x: x["email"].lower())

    # Combine lists with current user at the top
    users = ([current_user_data] if current_user_data else []) + other_users

    # Modify form choices based on user role
    if not is_admin:
        form.role.choices = [
            choice for choice in form.role.choices if choice[0] != "admin"
        ]
        users = [user for user in users if user["role"] != "admin"]

    return render_template(
        "add_user.html",
        form=form,
        users=users,
        is_admin=is_admin,
        current_user_email=current_user.email,
        missing_from_sheet=missing_from_sheet,
        missing_from_db=missing_from_db,
    )


@blueprint.route("/run/update_user_role", methods=["POST"])
@admin_or_editor_required
@login_required
def update_user_role():
    data = request.json
    email = data.get("email")
    new_role = data.get("role")
    tournament_id = data.get("tournament_id")
    access = (
        db.session.query(Access)
        .filter_by(user_email=email, tournament_id=tournament_id)
        .first()
    )

    if access:
        try:
            # Check if the current user is an admin for this tournament
            is_admin = current_user.live_tournament_role == Role.admin
            # Prevent non-admin users from changing any admin role
            if not is_admin and (new_role == "admin" or access.role == Role.admin):
                return jsonify(
                    {
                        "success": False,
                        "error": "You don't have permission to change admin role",
                    }
                )
            access.role = Role[new_role]
            db.session.commit()
            return jsonify({"success": True, "current_role": new_role})
        except Exception as e:
            db.session.rollback()
            return jsonify(
                {"success": False, "current_role": access.role.value, "error": str(e)}
            )
    else:
        return jsonify(
            {"success": False, "error": "User not found for this tournament"}
        )


@blueprint.route("/run/remove_user_access", methods=["POST"])
@admin_or_editor_required
@login_required
def remove_user_access():
    data = request.json
    email = data.get("email")
    tournament_id = data.get("tournament_id")

    # Check if the current user is trying to remove themselves
    if email == current_user.email:
        return jsonify({"success": False, "error": "You cannot remove yourself"})

    # Check if the current user is an admin for this tournament
    is_admin = current_user.live_tournament_role == Role.admin

    access = (
        db.session.query(Access)
        .filter_by(user_email=email, tournament_id=tournament_id)
        .first()
    )

    if access:
        try:
            # Prevent non-admin users from removing admin access
            if not is_admin and access.role == Role.admin:
                return jsonify(
                    {
                        "success": False,
                        "error": "You don't have permission to remove admin access",
                    }
                )

            db.session.delete(access)
            db.session.commit()

            # Revoke Google Sheet access
            tournament = db.session.query(Tournament).get(tournament_id)

            revoke_result = googlesheet.revoke_sheet_access(
                tournament.google_doc_id, email
            )

            if revoke_result == True:
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "error": revoke_result})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)})
    else:
        return jsonify(
            {"success": False, "error": "User access not found for this tournament"}
        )


@blueprint.route("/run/fix_access", methods=["POST"])
@admin_or_editor_required
@login_required
def fix_access():
    data = request.json
    email = data.get("email").lower()
    action = data.get("action")
    tournament_id = data.get("tournament_id")

    tournament = db.session.query(Tournament).get(tournament_id)

    if action == "add_to_sheet":
        result = googlesheet.share_sheet(tournament.google_doc_id, email, notify=False)
        if result == True:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": result})

    elif action == "add_to_db":
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
        access = Access(email, tournament=tournament, role=Role.scorer)
        db.session.add(access)
        try:
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)})

    elif action == "remove":
        db_removed = False
        sheet_removed = False
        error_message = ""

        # Remove database access
        access = (
            db.session.query(Access)
            .filter_by(user_email=email, tournament_id=tournament_id)
            .first()
        )
        if access:
            try:
                db.session.delete(access)
                db.session.commit()
                db_removed = True
            except Exception as e:
                db.session.rollback()
                error_message += f"Failed to remove database access: {str(e)}. "

        sheet_result = googlesheet.revoke_sheet_access(tournament.google_doc_id, email)
        if sheet_result == True:
            sheet_removed = True
        else:
            error_message += f"Failed to remove sheet access: {sheet_result}. "

        # Determine the overall result
        if db_removed or sheet_removed:
            success_message = "Access removed successfully. "
            if db_removed:
                success_message += "Database access removed. "
            if sheet_removed:
                success_message += "Sheet access removed. "
            if error_message:
                success_message += f"Some errors occurred: {error_message}"
            return jsonify({"success": True, "message": success_message.strip()})
        else:
            return jsonify(
                {
                    "success": False,
                    "error": f"Failed to remove any access. {error_message.strip()}",
                }
            )

    else:
        return jsonify({"success": False, "error": "Invalid action"})


@blueprint.route("/run/sync_access", methods=["POST"])
@admin_required
@login_required
def sync_access_route():
    tournament_id = current_user.live_tournament_id

    try:
        sync_access(tournament_id)
        flash("Access synchronized successfully", "success")
    except Exception as e:
        flash(f"Failed to synchronize access: {str(e)}", "error")
        logging.error(
            f"Exception occurred while synchronizing access: {str(e)}",
            exc_info=True,
        )

    # Redirect back to the referring page
    return redirect(request.referrer or url_for("user_management.add_user_get"))


@admin_required
@login_required
def sync_access(tournament_id):
    tournament = db.session.query(Tournament).get(tournament_id)
    sheet_users = googlesheet.get_sheet_users(tournament.google_doc_id)
    db_users = db.session.query(Access).filter_by(tournament_id=tournament_id).all()
    sheet_emails = {user["email"].lower() for user in sheet_users}
    db_emails = {access.user_email.lower() for access in db_users}

    # Add missing users to the database
    for email in sheet_emails - db_emails:
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
        access = Access(email, tournament=tournament, role=Role.scorer)
        db.session.add(access)

    # Remove extra users from the database
    for email in db_emails - sheet_emails:
        access = (
            db.session.query(Access)
            .filter_by(user_email=email, tournament_id=tournament_id)
            .first()
        )
        if access:
            db.session.delete(access)

    db.session.commit()

    # Update Google Sheet access
    for email in db_emails - sheet_emails:
        googlesheet.share_sheet(tournament.google_doc_id, email, notify=False)

    for email in sheet_emails - db_emails:
        googlesheet.revoke_sheet_access(tournament.google_doc_id, email)


@blueprint.route("/run/delete_user", methods=["POST"])
@superadmin_required
@login_required
def delete_user():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"success": False, "error": "Email is required"})

    try:
        user = db.session.query(User).filter_by(email=email).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "User not found"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})
