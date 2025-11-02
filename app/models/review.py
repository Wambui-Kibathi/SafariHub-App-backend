from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates

Base = declarative_base()

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    destination_id = Column(Integer, ForeignKey('destinations.id'), nullable=False)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    destination = relationship("Destination", back_populates="reviews")
    booking = relationship("Booking", back_populates="review")
    
    @validates('rating')
    def validate_rating(self, key, rating):
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return rating
    
    def to_dict(self):
        try:
            return {
                'id': self.id,
                'user_id': self.user_id,
                'destination_id': self.destination_id,
                'booking_id': self.booking_id,
                'rating': self.rating,
                'comment': self.comment,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            }
        except (AttributeError, TypeError):
            raise ValueError("Invalid review data for serialization")