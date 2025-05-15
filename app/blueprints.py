# app/blueprints.py
from app.routes.main_routes import main
from app.routes.auth_routes import auth
from app.routes.upload_routes import upload_bp
from app.routes.share_routes import share_bp
from app.routes.user_routes import user_bp
from app.routes.notification_routes import notify_bp
from app.routes.history_routes import history_bp

def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(upload_bp, url_prefix="/upload")
    app.register_blueprint(share_bp, url_prefix="/share")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(notify_bp, url_prefix="/notifications")
    app.register_blueprint(history_bp, url_prefix="/history")
