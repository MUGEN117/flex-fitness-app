from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from flask_login import LoginManager   # ✅ Add this import

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()          # ✅ Add this

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)          # ✅ Connect Flask-Login to your app
    
    login_manager.login_view = "auth.login_trainer"  # Redirect unauthorized users
    login_manager.login_message_category = "warning"

    # Import blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.member import member_bp
    from app.routes.trainer import trainer_bp
    from app.routes.exercise import template_bp
    from app.routes.profile import profile_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(trainer_bp)
    app.register_blueprint(template_bp)
    app.register_blueprint(profile_bp)

    return app
