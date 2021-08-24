# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CESNET.
#
# nr-dataset-metadata is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataset record schemas."""
from datetime import datetime
from functools import partial

from flask_babelex import lazy_gettext as _
from flask_security import current_user
from invenio_records_rest.schemas import StrictKeysMixin
from marshmallow import fields, pre_load, validate, validates, Schema, validates_schema
from marshmallow.fields import List
from marshmallow_utils.fields import (
    EDTFDateString,
    IdentifierSet,
    NestedAttribute,
    SanitizedHTML,
    SanitizedUnicode,
)
from oarepo_invenio_model.marshmallow import (
    InvenioRecordMetadataFilesMixin,
    InvenioRecordMetadataSchemaV1Mixin,
)
from oarepo_multilingual.marshmallow import MultilingualStringV2
from oarepo_taxonomies.marshmallow import TaxonomyField

from oarepo_rdm_records.marshmallow.access import AccessSchema
from oarepo_rdm_records.marshmallow.dates import DateSchema
from oarepo_rdm_records.marshmallow.identifier import (
    IdentifierSchema,
    RelatedIdentifierSchema,
)
from oarepo_rdm_records.marshmallow.mixins import RightsMixin, TitledMixin
from oarepo_rdm_records.marshmallow.person import ContributorSchema, CreatorSchema
from oarepo_rdm_records.marshmallow.pids import PIDSchema
from oarepo_rdm_records.marshmallow.reference import ReferenceSchema
from oarepo_rdm_records.marshmallow.resource import ResourceType
from oarepo_rdm_records.marshmallow.subject import SubjectSchema


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
            "required": [
                _('Invalid value. Choose one of {NAMES}.').format(
                    NAMES=NAMES)]
        }
    )

    @validates_schema
    def validate_names(self, data, **kwargs):
        """Validate names based on type."""
        #todo require title type


class DataSetMetadataSchemaV2(InvenioRecordMetadataFilesMixin,
                              InvenioRecordMetadataSchemaV1Mixin,
                              StrictKeysMixin):
    """DataSet metaddata schema."""

    # resource_type = ResourceType(required=True)
    # creators = fields.List(
    #     fields.Nested(CreatorSchema),
    #     required=True,
    #     validate=validate.Length(
    #         min=1, error=_("Missing data for required field.")
    #     )
    # )
    # creator = SanitizedUnicode()
    titles = fields.Nested(TitlesSchema) #..
    # additional_titles = List(MultilingualStringV2())
    # publisher = SanitizedUnicode()
    # publication_date = EDTFDateString(required=True)
    # subjects = List(fields.Nested(SubjectSchema))
    # contributors = List(fields.Nested(ContributorSchema))
    # dates = List(fields.Nested(DateSchema))
    # languages = TaxonomyField(mixins=[TitledMixin], many=True)
    # # alternate identifiers
    # identifiers = IdentifierSet(
    #     fields.Nested(partial(IdentifierSchema, fail_on_unknown=False))
    # )
    # related_identifiers = List(fields.Nested(RelatedIdentifierSchema))
    # version = SanitizedUnicode()
    # rights = TaxonomyField(mixins=[TitledMixin, RightsMixin], many=True)
    # abstract = MultilingualStringV2(required=True)  # WARNING: May contain user-input HTML
    # additional_descriptions = fields.List(MultilingualStringV2())
    # references = fields.List(fields.Nested(ReferenceSchema))
    # pids = fields.Dict(keys=fields.String(), values=fields.Nested(PIDSchema))
    # access = NestedAttribute(AccessSchema)
    # keywords = List(SanitizedUnicode())
    #
    # @pre_load
    # def sanitize_html_fields(self, data, **kwargs):
    #     """Sanitize fields that may contain user-input HTML strings."""
    #     if 'abstract' in data:
    #         for lang, val in data.get('abstract').items():
    #             raw = data['abstract'][lang]
    #             data['abstract'][lang] = SanitizedHTML()._deserialize(raw, 'abstract', data)
    #
    #     return data
    #
    # @pre_load
    # def set_created(self, data, **kwargs):
    #     """Set created timestamp if not already set."""
    #     dates = data.get('dates') or []
    #     created = None
    #
    #     for dat in dates:
    #         if dat.get('type', '') == 'created':
    #             created = dat.get('date')
    #
    #     if not created:
    #         dates.append({
    #             'date': datetime.today().strftime('%Y-%m-%d'),
    #             'type': 'created'
    #         })
    #         data['dates'] = dates
    #
    #     return data
    #
    # @pre_load
    # def set_creator(self, data, **kwargs):
    #     """Set creator to record metadata if not known."""
    #     if not data.get('creator'):
    #         if current_user and current_user.is_authenticated:
    #             data['creator'] = current_user.email
    #         else:
    #             data['creator'] = 'anonymous'
    #     return data
    #
    # @validates('pids')
    # def validate_pids(self, value):
    #     """Validate the keys of the pids are supported providers."""
    #     for scheme, pid_attrs in value.items():
    #         # The required flag applies to the identifier value
    #         # It won't fail for empty allowing the components to reserve one
    #         id_schema = IdentifierSchema(
    #             fail_on_unknown=False, identifier_required=True)
    #         id_schema.load({
    #             "scheme": scheme,
    #             "identifier": pid_attrs.get("identifier")
    #         })
