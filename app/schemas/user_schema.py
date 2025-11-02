from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True, validate=validate.Length(min=2))
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=6))
    role = fields.Str(required=True, validate=validate.OneOf(["traveler", "guide", "admin"]))
    profile_pic = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)