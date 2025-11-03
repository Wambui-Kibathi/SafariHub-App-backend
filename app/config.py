import os
from datetime import timedelta

class Config:
    # General Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "safarihub-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///safarihub.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "safarihub-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Mail Configuration (SendGrid SMTP)
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("SENDGRID_USERNAME")
    MAIL_PASSWORD = os.getenv("SENDGRID_API_KEY")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@safarihub.com")

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    # PayPal Configuration
    PAYSTACK_PUBLIC_KEY = os.getenv("PAYPAL_CLIENT_ID")
    PAYSTACK_SECRET_KEY = os.getenv("PAYPAL_SECRET_KEY")
    PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")

    # Swagger Configuration
    SWAGGER = {
        "title": "SafariHub API",
        "uiversion": 3
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig
)
