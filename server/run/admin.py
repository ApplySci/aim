# -*- coding: utf-8 -*-

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from config import GOOGLE_CLIENT_EMAIL, OUR_EMAILS, TEMPLATE_ID
from create.write_sheet import googlesheet

blueprint = Blueprint('admin', __name__)

@blueprint.route('/admin/delete/<doc_id>', methods=['DELETE',])
@login_required
def delet_dis(doc_id):
    if current_user.email not in OUR_EMAILS:
        return "not found",  404
    if doc_id == TEMPLATE_ID:
        return "Sorry Dave, I can't do that", 403
    googlesheet.delete_sheet(doc_id)
    return "ok", 204


@blueprint.route('/admin/list')
@login_required
def superuser():
    if current_user.email not in OUR_EMAILS:
        return "not found",  404
    docs = googlesheet.list_sheets(GOOGLE_CLIENT_EMAIL)
    our_docs = [doc for doc in docs if doc['ours'] and \
                doc['id'] != TEMPLATE_ID]
    return render_template('adminlist.html', docs=our_docs)
