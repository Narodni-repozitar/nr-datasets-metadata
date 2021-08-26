# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""
from functools import partial

import idutils
from flask_babelex import lazy_gettext as _
from marshmallow import (
    Schema,
    ValidationError,
    fields,
    post_load,
    validate,
    validates_schema,
)
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema
from oarepo_taxonomies.marshmallow import TaxonomyField

#from oarepo_rdm_records.config import RDM_RECORDS_IDENTIFIERS_SCHEMES todo: marhsmallow unitls change!!
from oarepo_rdm_records.marshmallow.mixins import TitledMixin


class AffiliationSchema(Schema):
    """Affiliation of a creator/contributor."""

    name = SanitizedUnicode(required=True)
    identifiers = IdentifierSet(
        fields.Nested(IdentifierSchema
                      #, allowed_schemes=RDM_RECORDS_IDENTIFIERS_SCHEMES
                      ),
    )


class PersonOrOrganizationSchema(Schema):
    """Person or Organization schema."""

    NAMES = [
        "organizational",
        "personal"
    ]

    type = SanitizedUnicode(
        required=True,
        validate=validate.OneOf(
            choices=NAMES,
            error=_(f'Invalid value. Choose one of {NAMES}.')
        ),
        error_messages={
            # NOTE: [] needed to mirror above error message
            "required": _(f'Invalid value. Choose one of {NAMES}.')
        }
    )
    name = SanitizedUnicode()
    given_name = SanitizedUnicode()
    family_name = SanitizedUnicode()
    identifiers = IdentifierSet(
        fields.Nested(partial(
            IdentifierSchema,
            # It is intendedly allowing org schemes to be sent as personal
            # and viceversa. This is a trade off learnt from running
            # Zenodo in production.
            allowed_schemes = {
                            "orcid": {"label": "ORCID", "validator": idutils.is_orcid},
                            "isni": {"label": "ISNI", "validator": idutils.is_isni},
                            "gnd": {"label": "GND", "validator": idutils.is_gnd},
                            "ror": {"label": "ROR", "validator": idutils.is_ror}

                        }
        ))
    )

    @validates_schema
    def validate_names(self, data, **kwargs):
        """Validate names based on type."""
        if data['type'] == "personal":
            if not (data.get('given_name') or data.get('family_name')):
                messages = [_("Family name or given name must be filled.")]
                raise ValidationError({
                    "given_name": messages,
                    "family_name": messages
                })

        elif data['type'] == "organizational":
            if not data.get('name'):
                messages = [_('Name cannot be blank.')]
                raise ValidationError({"name": messages})

    @post_load
    def update_names(self, data, **kwargs):
        """Update names for organization / person.

        Fill name from given_name and family_name if person.
        Remove given_name and family_name if organization.
        """
        if data["type"] == "personal":
            names = [data.get("family_name"), data.get("given_name")]
            data["name"] = ", ".join([n for n in names if n])

        elif data['type'] == "organizational":
            if 'family_name' in data:
                del data['family_name']
            if 'given_name' in data:
                del data['given_name']

        return data


class ContributorSchema(Schema):
    """Contributor schema."""

    person_or_org = fields.Nested(PersonOrOrganizationSchema)
    role = TaxonomyField(mixins=[TitledMixin])
    affiliations = fields.List(fields.Nested(AffiliationSchema))

    @validates_schema
    def validate_role(self, data, **kwargs):
        """Validate role."""
        # TODO: taxonomy validation?


class CreatorSchema(Schema):
    """Creator schema."""

    person_or_org = fields.Nested(PersonOrOrganizationSchema, required=True)
    role = TaxonomyField(mixins=[TitledMixin])
    affiliations = fields.List(fields.Nested(AffiliationSchema))

    @validates_schema
    def validate_role(self, data, **kwargs):
        """Validate role."""
        # TODO: taxonomy validation?
        # if 'role' in data:
