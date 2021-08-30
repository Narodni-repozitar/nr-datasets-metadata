from functools import partial

from marshmallow_utils.schemas import IdentifierSchema

ObjectPIDSchema = partial(IdentifierSchema, allowed_schemes=(
    "DOI",
    "Handle",
    "ISBN",
    "ISSN",
    "RIV"
))
