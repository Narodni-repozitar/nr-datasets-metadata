from functools import partial

from marshmallow import Schema, fields
from marshmallow_utils.fields import EDTFDateString
from marshmallow_utils.schemas import IdentifierSchema
from oarepo_multilingual.marshmallow import MultilingualStringV2
from oarepo_taxonomies.marshmallow import TaxonomyField

from nr_datasets_metadata.marshmallow.constants import RDM_RECORDS_IDENTIFIERS_SCHEMES
from nr_datasets_metadata.marshmallow.subschemas.date import StringDateField, DateWithdrawn
from nr_datasets_metadata.marshmallow.subschemas.funding import FundingReference
from nr_datasets_metadata.marshmallow.subschemas.geo import GeoLocationSchema
from nr_datasets_metadata.marshmallow.subschemas.person import CreatorSchema, ContributorSchema
from nr_datasets_metadata.marshmallow.subschemas.pids import PersistentIdentifierSchema
from nr_datasets_metadata.marshmallow.subschemas.related import RelatedItemSchema
from nr_datasets_metadata.marshmallow.subschemas.taxonomy import SingleValuedMixin
from nr_datasets_metadata.marshmallow.subschemas.titles import TitlesList
from nr_datasets_metadata.marshmallow.subschemas.utils import no_duplicates, not_empty


DATE_RANGE_FIELDS = ['dateCreated', 'dateCollected']


# TODO: this needs to be made more generic before we can support more schemas
def date_ranges_to_index(sender, json=None, record=None,
                         index=None, doc_type=None, arguments=None, **kwargs):

    for dr in DATE_RANGE_FIELDS:
        if dr in json:
            dates = json[dr].split('/', 1)
            if len(dates) == 1:
                since = until = dates[0]
            else:
                since, until = dates

            json[dr] = {
                'gte': since,
                'lte': until
            }

    return json


class DataSetMetadataSchemaV3(Schema):
    titles = TitlesList()
    creators = fields.List(fields.Nested(CreatorSchema()))
    contributors = fields.List(fields.Nested(ContributorSchema()))

    resourceType = TaxonomyField(mixins=[SingleValuedMixin])

    dateAvailable = EDTFDateString()

    dateModified = EDTFDateString()
    dateCreated = EDTFDateString() # Can be a date range
    dateCollected = EDTFDateString() # Can be a date range
    dateValidTo = EDTFDateString()
    dateWithdrawn = EDTFDateString()

    keywords = fields.List(MultilingualStringV2(), validate=[no_duplicates])

    subjectCategories = TaxonomyField(required=True, many=True)

    language = TaxonomyField(many=True)

    notes = fields.List(fields.String(), validate=[no_duplicates])

    abstract = MultilingualStringV2(required=True)

    methods = MultilingualStringV2()    # TODO: singular or plural ?

    technicalInfo = MultilingualStringV2()

    rights = TaxonomyField()

    publisher = TaxonomyField(required=True, many=True)

    accessRights = TaxonomyField(required=True)

    relatedItems = fields.List(fields.Nested(RelatedItemSchema))

    fundingReferences = fields.List(fields.Nested(FundingReference), validate=[no_duplicates])

    version = fields.String()

    geoLocations = fields.List(fields.Nested(GeoLocationSchema))

    persistentIdentifiers = fields.List(
        fields.Nested(partial(PersistentIdentifierSchema, allowed_schemes=RDM_RECORDS_IDENTIFIERS_SCHEMES)),
        validate=[no_duplicates, not_empty]
        )
