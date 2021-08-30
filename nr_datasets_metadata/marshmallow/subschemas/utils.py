import json

from marshmallow import ValidationError
from flask_babelex import lazy_gettext as _


def no_duplicates(value):
    if value is None:
        return value
    v = [json.dumps(x, sort_keys=True) for x in value]
    if len(set(v)) != len(value):
        raise ValidationError(message=_('Duplicates not allowed'))
    return value


def not_empty(value):
    if not value:
        raise ValidationError(message=_('Must not be empty'))
    return value
