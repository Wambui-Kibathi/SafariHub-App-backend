from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
import enum

Base = declarative_base()

class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    destination_id = Column(Integer, ForeignKey('destinations.id'), nullable=False)
    booking_date = Column(DateTime, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    guests = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    special_requests = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    destination = relationship("Destination", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    
    @validates('guests')
    def validate_guests(self, key, guests):
        if guests < 1:
            raise ValueError("Guests must be at least 1")
        return guests
    
    @validates('total_price')
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price
    
    def to_dict(self):
        try:
            return {
                'id': self.id,
                'user_id': self.user_id,
                'destination_id': self.destination_id,
                'booking_date': self.booking_date.isoformat(),
                'start_date': self.start_date.isoformat(),
                'end_date': self.end_date.isoformat(),
                'guests': self.guests,
                'total_price': self.total_price,
                'status': self.status.value,
                'special_requests': self.special_requests,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            }
        except (AttributeError, TypeError):
            raise ValueError("Invalid booking data for serialization")