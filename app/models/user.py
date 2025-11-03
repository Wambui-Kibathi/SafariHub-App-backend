from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="traveler")  # traveler, guide, admin
    profile_pic = db.Column(db.String(255))  # Cloudinary URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.full_name} ({self.role})>"

    # Password handling
    @property
    def password(self):
        """Prevent password from being read directly."""
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plaintext_password):
        """Hash password before saving."""
        self.password_hash = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        """Verify a user's password."""
        return check_password_hash(self.password_hash, plaintext_password)

    # Role helpers
    def is_traveler(self):
        return self.role == "traveler"

    def is_guide(self):
        return self.role == "guide"

    def is_admin(self):
        return self.role == "admin"
