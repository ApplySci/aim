# -*- coding: utf-8 -*-
"""
user account self-management
"""

from flask import Blueprint, redirect, session, url_for, render_template, flash
from flask_login import login_required, login_user, logout_user, current_user

from oauth_setup import db, logging, login_manager, oauth
from models import User

blueprint = Blueprint("accounts", __name__)
messages_by_user = {}


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.query(User).get(user_id)
    except:
        return None


@blueprint.route("/account/delete", methods=["GET", "POST"])
@login_required
def delete_account():
    # TODO this doesn't do anything yet. It will, in time
    return render_template("delete_account.html", email=current_user.email)


@blueprint.route("/login")
def login():
    redirect_uri = url_for("accounts.authorized", _external=True, _scheme="https")
    try:
        return oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        logging.warning(f"Error in login: {str(e)}")
        return redirect(url_for('root.index'))


@blueprint.route("/logout")
def logout():
    session.clear()
    logout_user()
    return redirect("/")


@blueprint.route("/auth/")
def authorized():
    try:
        token = oauth.google.authorize_access_token()
        resp = oauth.google.get("userinfo")
        user_info = resp.json()
        user = db.session.query(User).get(user_info["email"])
        if user and user.is_active:
            login_user(user)
            session.pop("_flashes", None)
            return redirect("/run/")
    except Exception as e:
        logging.warning(f"Error in authorization: {str(e)}")
    return logout()
