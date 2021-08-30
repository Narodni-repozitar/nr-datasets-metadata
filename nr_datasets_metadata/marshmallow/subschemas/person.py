# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from flask_babelex import lazy_gettext as _
from marshmallow import (
    ValidationError, Schema,
)
from oarepo_rdm_records.marshmallow.mixins import TitledMixin
from oarepo_taxonomies.marshmallow import TaxonomyField

from nr_datasets_metadata.marshmallow.subschemas.authority import AuthoritySchema


class AffiliationRequiredMixin(Schema):
    def load(self, data, *, many=None, partial=None, unknown=None, **kwargs):
        data = super().load(data, many=many, partial=partial, unknown=unknown)

        affilliation = data.get('affiliation', None)
        if not affilliation:
            raise ValidationError(
                message=_('Required affiliation field not found')
            )
        if not isinstance(affilliation, (list, tuple)):
            raise ValidationError(
                message=_('affiliation must be a taxonomy')
            )
        if not len(affilliation):
            raise ValidationError(
                message=_('affiliation is not set up')
            )

        return data


class ContributorSchema(AffiliationRequiredMixin, AuthoritySchema):
    """Contributor schema."""

    role = TaxonomyField(mixins=[TitledMixin], required=True)


class CreatorSchema(AffiliationRequiredMixin, AuthoritySchema):
    """Creator schema."""
