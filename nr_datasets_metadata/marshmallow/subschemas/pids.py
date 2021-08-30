from marshmallow import fields
from marshmallow_utils.schemas import IdentifierSchema


class PersistentIdentifierSchema(IdentifierSchema):
    status = fields.Str(required=True)
