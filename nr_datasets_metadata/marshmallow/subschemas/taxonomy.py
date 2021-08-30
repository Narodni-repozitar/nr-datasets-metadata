from marshmallow import ValidationError, validates_schema, Schema
from flask_babelex import lazy_gettext as _


class SingleValuedMixin(Schema):
    @validates_schema(pass_many=True)
    def validate(self, value, *args, **kwargs):
        if value and isinstance(value, (list, tuple)) and len(value) > 1:
            raise ValidationError(message=_('Only one value required'))
        return value
