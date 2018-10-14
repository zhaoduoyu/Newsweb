from flask import Blueprint, session, redirect, request,url_for

admin_blue = Blueprint('admin_blue', __name__, url_prefix="/admin")

from . import views


@admin_blue.before_request
def is_admin_login():
    is_admin = session.get('is_admin', False)

    print(is_admin)

    print(url_for("admin_blue.admin_index"))
    if not is_admin and request.url.endswith(url_for("admin_blue.admin_index")):
        return redirect("/")