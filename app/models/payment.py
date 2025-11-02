from datetime import datetime
from ..extensions import db

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, success, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Payment {self.reference} - {self.status}>"
