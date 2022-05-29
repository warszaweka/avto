from flask import Blueprint, render_template

admin = Blueprint("admin", __name__)


@admin.route("/")
def root():
    return render_template("root.html")
