from functools import partial

import idutils
from invenio_records_rest.schemas import StrictKeysMixin
from marshmallow import fields, Schema, validate, validates, ValidationError
from marshmallow.validate import Range
from marshmallow_utils.fields import SanitizedUnicode, EDTFDateString
from oarepo_invenio_model.marshmallow import InvenioRecordMetadataSchemaV1Mixin, InvenioRecordMetadataFilesMixin
from oarepo_multilingual.marshmallow import MultilingualStringV2
from flask_babelex import lazy_gettext as _
from oarepo_taxonomies.marshmallow import TaxonomyField
from marshmallow_utils.schemas import IdentifierSchema as IS
def always_valid(identifier):
    """Gives every identifier as valid."""
    return True
RDM_RECORDS_IDENTIFIERS_SCHEMES ={
        "ark": {
            "label": _("ARK"),
            "validator": idutils.is_ark,
            "datacite": "ARK"
        },
        "arxiv": {
            "label": _("arXiv"),
            "validator": idutils.is_arxiv,
            "datacite": "arXiv"
        },
        "bibcode": {
            "label": _("Bibcode"),
            "validator": idutils.is_ads,
            "datacite": "bibcode"
        },
        "doi": {
            "label": _("DOI"),
            "validator": idutils.is_doi,
            "datacite": "DOI"
        },
        "ean13": {
            "label": _("EAN13"),
            "validator": idutils.is_ean13,
            "datacite": "EAN13"
        },
        "eissn": {
            "label": _("EISSN"),
            "validator": idutils.is_issn,
            "datacite": "EISSN"
        },
        "handle": {
            "label": _("Handle"),
            "validator": idutils.is_handle,
            "datacite": "Handle"
        },
        "igsn": {
            "label": _("IGSN"),
            "validator": always_valid,
            "datacite": "IGSN"
        },
        "isbn": {
            "label": _("ISBN"),
            "validator": idutils.is_isbn,
            "datacite": "ISBN"
        },
        "issn": {
            "label": _("ISSN"),
            "validator": idutils.is_issn,
            "datacite": "ISSN"
        },
        "istc": {
            "label": _("ISTC"),
            "validator": idutils.is_istc,
            "datacite": "ISTC"
        },
        "lissn": {
            "label": _("LISSN"),
            "validator": idutils.is_issn,
            "datacite": "LISSN"
        },
        "lsid": {
            "label": _("LSID"),
            "validator": idutils.is_lsid,
            "datacite": "LSID"
        },
        "pmid": {
            "label": _("PMID"),
            "validator": idutils.is_pmid,
            "datacite": "PMID"
        },
        "purl": {
            "label": _("PURL"),
            "validator": idutils.is_purl,
            "datacite": "PURL"
        },
        "upc": {
            "label": _("UPC"),
            "validator": always_valid,
            "datacite": "UPC"
        },
        "url": {
            "label": _("URL"),
            "validator": idutils.is_url,
            "datacite": "URL"
        },
        "urn": {
            "label": _("URN"),
            "validator": idutils.is_urn,
            "datacite": "URN"
        },
        "w3id": {
            "label": _("W3ID"),
            "validator": always_valid,
            "datacite": "w3id"
        },
    }
def _no_duplicates(value_list):
    str_list = [str(value) for value in value_list]
    return len(value_list) == len(set(str_list))

def _only_one_item(value_list):
    return len(value_list) == 1

def _more_than_one_item(value_list):
    return len(value_list) >= 1

class DateWithdrawn(Schema):
    date = EDTFDateString()
    dateInformation = fields.String()

class FundingReference(Schema):
    projectID = fields.String(required=True)
    projectName = fields.String()
    fundingProgram = fields.String()
    funder = TaxonomyField(required=True)
class TitlesSchema(Schema):
    """Titles of the object/work."""
    NAMES = [
        "mainTitle",
        "alternativeTitle",
        "subtitle",
        "other"
    ]
    title = MultilingualStringV2(required=True)
    title_type = SanitizedUnicode(
        required=True,
        validate=validate.OneOf(
            choices=NAMES,
            error=_('Invalid value. Choose one of {NAMES}.')
            .format(NAMES=NAMES)
        ),
        error_messages={
            # [] needed to mirror error message above
            "required": _('Invalid value. Choose one of {NAMES}.').format(NAMES=NAMES)
        }
    )
class TitledMixin:
    """Mixin that adds a multilingual title field to Schema."""

    title = MultilingualStringV2()


class GeoLocationPointSchema(Schema):
    pointLongitude = fields.Integer(validate=Range(min=-180, min_inclusive=True, max=180, max_inclusive=True))
    pointLatitude = fields.Integer(validate=Range(min=-90, min_inclusive=True, max=90, max_inclusive=True))

class GeoLocationSchema(Schema):
    geoLocationPlace = fields.String(required=True)
    geoLocationPoint = fields.Nested(GeoLocationPointSchema)


class IdentifierSchema(IS):
    """Identifier schema with optional status field."""
    status = SanitizedUnicode(required=True)

class DataSetMetadataSchemaV3(InvenioRecordMetadataFilesMixin,
                              InvenioRecordMetadataSchemaV1Mixin,
                              StrictKeysMixin):
    titles = fields.List(fields.Nested(TitlesSchema))

    @validates('titles')
    def validate_titles(self, value):
        """Validate types of titles."""
        main_title = False
        for item in value:
            type = item['title_type']
            if type == "mainTitle":
                main_title = True
        if not main_title:
            raise ValidationError({
                "title_type": _("At least one title must have type mainTitle")
            })
        if not _no_duplicates(value):
            raise ValidationError({
                "titles": _("Unique items required")
            })
    #creator todo
    #contributors todo
    resourceType = TaxonomyField()

    @validates('resourceType')
    def validate_res(self, value):
        if not _only_one_item(value):
            raise ValidationError({
                "resource_type": _("Only one value required")
            })

    dateAvailable = fields.String() #todo date

    @validates('dateAvailable')
    def validate_dates(self, value):
        pass  # todo check if year, yearmonth, date, datetime


    dateModified = fields.String() #todo date
    dateCollected = EDTFDateString()
    dateValidTo = fields.String() #todo date
    dateWithdrawn = fields.Nested(DateWithdrawn)

    keywords = MultilingualStringV2()
    subjectCategories = TaxonomyField()

    @validates('subjectCategories')
    def validate_subjectCategories(self, value):
        if not _no_duplicates(value):
            raise ValidationError({
                "subjectCategories": _("Unique items required")
            })

    language = TaxonomyField()

    @validates('language')
    def validate_language(self, value):
        if not _no_duplicates(value):
            raise ValidationError({
                "language": _("Unique items required")
            })

    rights = TaxonomyField()

    @validates('rights')
    def validate_rights(self, value):
        if not _no_duplicates(value):
            raise ValidationError({
                "rights": _("Unique items required")
            })

    accessRights = TaxonomyField()

    @validates('accessRights')
    def validate_accessRights(self, value):
        if not _no_duplicates(value):
            raise ValidationError({
                "accessRights": _("Unique items required")
            })

    note = fields.List(fields.String())

    @validates('note')
    def validate_note(self, value):
        if not _no_duplicates(value):
            raise ValidationError({
                "note": _("Unique items required")
            })

    abstract = MultilingualStringV2()

    @validates('abstract')
    def validate_abstract(self, value):
        if not _no_duplicates(value):
            raise ValidationError({
                "abstract": _("Unique items required")
            })

    methods = MultilingualStringV2()

    @validates('methods')
    def validate_methods(self, value):
        if not _no_duplicates(value):
            raise ValidationError({
                "methods": _("Unique items required")
            })

    technicalInfo = MultilingualStringV2()

    @validates('technicalInfo')
    def validate_technicalInfo(self, value):
        if not _no_duplicates(value):
            raise ValidationError({
                "technicalInfo": _("Unique items required")
            })

    # todo relatedItems

    fundingReference = fields.List(fields.Nested(FundingReference))

    @validates('fundingReference')
    def validate_fundingReference(self, value):
        if not _no_duplicates(value):
            raise ValidationError({
                "fundingReference": _("Unique items required")
            })
    version = fields.String()

    geoLocation = fields.List(fields.Nested(GeoLocationSchema))
    InvenioID = fields.String()
    persistentIdentifiers =  fields.List(fields.Nested(partial(IdentifierSchema, allowed_schemes=RDM_RECORDS_IDENTIFIERS_SCHEMES))
    )

    @validates('persistentIdentifiers')
    def validate_persistentIdentifiers(self, value):
        if not _no_duplicates(value):
            raise ValidationError({
                "persistentIdentifiers": _("Unique items required")
            })
        if not _more_than_one_item(value):
            raise ValidationError({
                "resource_type": _("One or more values required")
            })
    #todo oarepo veci
    #todo _files
    #todo required
