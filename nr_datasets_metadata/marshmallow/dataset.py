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

from nr_datasets_metadata.marshmallow.constants import RDM_RECORDS_IDENTIFIERS_SCHEMES


def _no_duplicates(value_list):
    str_list = [str(value) for value in value_list]
    return len(value_list) == len(set(str_list))

def _only_one_item(value_list):
    return len(value_list) == 1

def _more_than_one_item(value_list):
    return len(value_list) >= 1

class FileNoteSchema(Schema):
    description = fields.String()
    type = fields.Boolean()

class FilesSchema(Schema):
    NAMES = ["fulltext",
                    "dataset",
                    "software",
                    "other"]
    versionID =fields.String()
    bucketID = fields.String()
    checksum = fields.String()
    size = fields.Integer()
    file_id = fields.String()
    key = fields.String()
    mimeType = fields.String()
    url = fields.Url()
    accessRights = TaxonomyField()
    fileNote = fields.List(fields.Nested(FileNoteSchema))
    objectType = SanitizedUnicode(
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

    dateAvailable = fields.String(required=True) #todo date

    @validates('dateAvailable')
    def validate_dates(self, value):
        pass  # todo check if year, yearmonth, date, datetime


    dateModified = fields.String() #todo date
    dateCollected = EDTFDateString()
    dateValidTo = fields.String() #todo date
    dateWithdrawn = fields.Nested(DateWithdrawn)

    keywords = MultilingualStringV2()
    subjectCategories = TaxonomyField(required=True)

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

    accessRights = TaxonomyField(required=True)

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

    abstract = MultilingualStringV2(required=True)

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
                "persistentIdentifiers": _("One or more values required")
            })
    #todo oarepo veci ??

    _files = fields.Nested(FilesSchema)
    #todo creator, contributor

