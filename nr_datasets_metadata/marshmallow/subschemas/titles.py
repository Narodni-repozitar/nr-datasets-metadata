from flask_babelex import lazy_gettext as _
from marshmallow import Schema, validate, fields, ValidationError
from marshmallow_utils.fields import SanitizedUnicode
from oarepo_multilingual.marshmallow import MultilingualStringV2


class TitlesSchema(Schema):
    """Titles of the object/work."""
    NAMES = [
        "mainTitle",
        "alternativeTitle",
        "subtitle",
        "other"
    ]
    title = MultilingualStringV2(required=True)
    titleType = SanitizedUnicode(
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


def _no_duplicates(value_list):
    str_list = [str(value) for value in value_list]
    return len(value_list) == len(set(str_list))


class TitlesList(fields.List):
    def __init__(self, **kwargs):
        super().__init__(fields.Nested(TitlesSchema), **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        value = super()._deserialize(value, attr, data, **kwargs)
        """Validate types of titles."""

        main_title = False

        for item in value:
            type = item['titleType']
            if type == "mainTitle":
                main_title = True

        if not main_title:
            raise ValidationError({
                "titleType": _("At least one title must have type mainTitle")
            })

        if not _no_duplicates(value):
            raise ValidationError({
                "titles": _("Unique items required")
            })

        return value
