import functools
import inspect

from flask_babelex import lazy_gettext as _
from marshmallow import Schema, fields, ValidationError
from marshmallow_oneofschema import OneOfSchema
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema
from oarepo_rdm_records.marshmallow.mixins import TitledMixin
from oarepo_taxonomies.marshmallow import TaxonomyField, TaxonomySchema


class AuthorityBaseSchema(Schema):
    full_name = SanitizedUnicode(data_key='fullName', attribute='fullName', required=True)
    name_type = SanitizedUnicode(data_key='nameType', attribute='nameType',
                                 choices=("Organizational", "Personal"), required=True)

    authority_identifiers = fields.List(
        fields.Nested(
            # TODO: IdentifierSchema performs checks for values which would fail here ...
            # TODO: setting fail_on_unknown disables this but should be handled by extending
            # TODO: the validation criteria
            IdentifierSchema(allowed_schemes=(
                "orcid",
                "scopusID",
                "researcherID",
                "czenasAutID",
                "vedidk",
                "institutionalID",
                "ISNI",
                "ROR",
                "ICO",
                "DOI"
            ), fail_on_unknown=False)), data_key='authorityIdentifiers', attribute='authorityIdentifiers')


class PersonSchema(AuthorityBaseSchema):
    name_type = SanitizedUnicode(data_key='nameType', attribute='nameType',
                                 choices=("Personal",))

    affiliation = TaxonomyField(mixins=[TitledMixin], required=False)


class OrganizationSchema(AuthorityBaseSchema, TaxonomySchema):
    name_type = SanitizedUnicode(data_key='nameType', attribute='nameType',
                                 choices=("Organizational",))


class AuthoritySchema(Schema):

    @functools.lru_cache(maxsize=2)
    def wrap_class(self, clz):
        # add extra fields to the class
        return type(clz.__name__, (clz,), self.declared_fields)

    def load(self, data, *, many=None, partial=None, unknown=None, **kwargs):
        if isinstance(data, (list, tuple)):
            types = set()
            for d in data:
                types.add(d['nameType'])
            if len(types) > 1:
                raise ValidationError(message=_('Can not mix personal and organizational authorities'))
            name_type = list(types)[0]
            if name_type == 'Personal':
                return self.wrap_class(PersonSchema)().load(data, many=True, partial=partial, unknown=unknown)
            else:
                return self.wrap_class(OrganizationSchema)().load(data, many=True, partial=partial, unknown=unknown)

        name_type = data['nameType']
        if name_type == 'Personal':
            return self.wrap_class(PersonSchema)().load(data, many=False, partial=partial, unknown=unknown)
        else:
            return self.wrap_class(OrganizationSchema)().load(data, many=False, partial=partial, unknown=unknown)
