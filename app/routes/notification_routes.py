from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user

from app.models import Notification, db

notify_bp = Blueprint("notify", __name__)

@notify_bp.route("/notifications")
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    return render_template("notifications.html", notifications=notifications)


@notify_bp.route("/mark_notification_read", methods=["POST"])
@login_required
def mark_notification_read():
    notifs = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for notif in notifs:
        notif.is_read = True
    db.session.commit()
    return jsonify({"success": True})


@notify_bp.route("/mark_notification_read_and_redirect")
@login_required
def mark_notification_read_and_redirect():
    notif = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.timestamp.desc()).first()
    if notif:
        notif.is_read = True
        db.session.commit()
    next_url = request.args.get("next") or url_for("main.index")
    return redirect(next_url)
