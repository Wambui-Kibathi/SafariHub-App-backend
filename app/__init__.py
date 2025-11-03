import os
from flask import Flask
from .extensions import db, ma, migrate, jwt, mail, cors
from .config import config_by_name

def create_app(config_name=None):
    app = Flask(__name__)

    # Load configuration
    env_config = config_by_name.get(config_name or os.getenv("FLASK_ENV", "development"))
    app.config.from_object(env_config)

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app, 
                  origins=["http://localhost:5173"], 
                  supports_credentials=True,
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])

    # Import all models so Flask-Migrate can detect them
    from .models.destination import Destination
    from .models.user import User
    from .models.booking import Booking
    from .models.payment import Payment
    from .models.review import Review

    # Import and register Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.traveler_routes import traveler_bp
    from .routes.guide_routes import guide_bp
    from .routes.admin_routes import admin_bp
    from .routes.destination_routes import destination_bp
    from .routes.booking_routes import booking_bp
    from .routes.payment_routes import payment_bp
    from .routes.upload_routes import upload_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(traveler_bp, url_prefix="/api/traveler")
    app.register_blueprint(guide_bp, url_prefix="/api/guide")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(destination_bp, url_prefix="/api/destinations")
    app.register_blueprint(booking_bp, url_prefix="/api/bookings")
    app.register_blueprint(payment_bp, url_prefix="/api/payments")
    app.register_blueprint(upload_bp, url_prefix="/api/uploads")

    return app
