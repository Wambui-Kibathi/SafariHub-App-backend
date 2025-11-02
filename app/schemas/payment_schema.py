from marshmallow import Schema, fields

class PaymentSchema(Schema):
    id = fields.Int(dump_only=True)
    booking_id = fields.Int(required=True)
    reference = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    amount = fields.Float(required=True)
    created_at = fields.DateTime(dump_only=True)
