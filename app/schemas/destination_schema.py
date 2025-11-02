from marshmallow import Schema, fields, validate

class DestinationSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2))
    country = fields.Str(required=True, validate=validate.Length(min=2))
    description = fields.Str(required=True)
    image_url = fields.Str(required=True)
    price = fields.Float(required=True)
    created_at = fields.DateTime(dump_only=True)
