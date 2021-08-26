from invenio_records_rest.schemas import StrictKeysMixin
from marshmallow import fields, Schema, validate, validates, ValidationError
from marshmallow_utils.fields import SanitizedUnicode
from oarepo_invenio_model.marshmallow import InvenioRecordMetadataSchemaV1Mixin, InvenioRecordMetadataFilesMixin
from oarepo_multilingual.marshmallow import MultilingualStringV2
from flask_babelex import lazy_gettext as _
from oarepo_taxonomies.marshmallow import TaxonomyField


def _no_duplicates(value_list):
    str_list = [str(value) for value in value_list]
    return len(value_list) == len(set(str_list))

def _only_one_item(value_list):
    return len(value_list) == 1
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
    def validate_titles(self, value):
        if not _only_one_item(value):
            raise ValidationError({
                "titles": _("Only one value required")
            })