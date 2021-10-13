from marshmallow import Schema, fields
from marshmallow import Schema, fields
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema
from oarepo_taxonomies.marshmallow import TaxonomyField

from nr_datasets_metadata.marshmallow.constants import RDM_RECORDS_IDENTIFIERS_SCHEMES
from nr_datasets_metadata.marshmallow.subschemas.date import StringDateField
from nr_datasets_metadata.marshmallow.subschemas.person import CreatorSchema, ContributorSchema
from nr_datasets_metadata.marshmallow.subschemas.utils import not_empty


class RelatedItemSchema(Schema):
    itemTitle = SanitizedUnicode(required=True)
    itemCreators = fields.List(fields.Nested(CreatorSchema), required=True, validate=[not_empty])
    itemContributors = fields.List(fields.Nested(ContributorSchema))
    itemPIDs = fields.List(fields.Nested(IdentifierSchema(
        allowed_schemes=RDM_RECORDS_IDENTIFIERS_SCHEMES
    )))
    itemURL = SanitizedUnicode()
    itemYear = StringDateField(required=True)

    itemVolume = SanitizedUnicode()
    itemIssue = SanitizedUnicode()
    itemStartPage = SanitizedUnicode()
    itemEndPage = SanitizedUnicode()

    itemPublisher = SanitizedUnicode()

    itemRelationType = TaxonomyField(required=True)
    itemResourceType = TaxonomyField(required=True)
