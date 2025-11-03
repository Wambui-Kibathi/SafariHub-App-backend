from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime

class BookingSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    destination_id = fields.Integer(required=True)
    booking_date = fields.DateTime(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    guests = fields.Integer(validate=validate.Range(min=1), load_default=1)
    total_price = fields.Float(required=True, validate=validate.Range(min=0))
    status = fields.String(dump_only=True)
    special_requests = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('start_date')
    def validate_start_date(self, value):
        if value <= datetime.now():
            raise ValidationError("Start date must be in the future")
    
    @validates('end_date')
    def validate_end_date(self, value):
        start_date = self.context.get('start_date')
        if start_date and value <= start_date:
            raise ValidationError("End date must be after start date")

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)