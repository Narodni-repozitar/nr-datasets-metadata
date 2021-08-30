from marshmallow import Schema, fields
from oarepo_taxonomies.marshmallow import TaxonomyField


class FundingReference(Schema):
    projectID = fields.String(required=True)
    projectName = fields.String()
    fundingProgram = fields.String()
    funder = TaxonomyField(required=True)

