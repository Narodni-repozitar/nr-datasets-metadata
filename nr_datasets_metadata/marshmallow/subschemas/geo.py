from marshmallow import Schema, fields
from marshmallow.validate import Range


class GeoLocationPointSchema(Schema):
    pointLongitude = fields.Integer(validate=Range(min=-180, min_inclusive=True, max=180, max_inclusive=True))
    pointLatitude = fields.Integer(validate=Range(min=-90, min_inclusive=True, max=90, max_inclusive=True))


class GeoLocationSchema(Schema):
    geoLocationPlace = fields.String(required=True)
    geoLocationPoint = fields.Nested(GeoLocationPointSchema)
