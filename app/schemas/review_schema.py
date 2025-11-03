from marshmallow import Schema, fields, validate
from app.schemas.user_schema import UserSchema
from app.schemas.booking_schema import BookingSchema

class ReviewSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    booking_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    
    user = fields.Nested(UserSchema, dump_only=True)
    booking = fields.Nested(BookingSchema, dump_only=True)
