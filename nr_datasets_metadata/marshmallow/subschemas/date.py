import re

from flask_babelex import lazy_gettext as _
from marshmallow import fields, ValidationError, Schema
from marshmallow.utils import from_iso_datetime, from_iso_date
from marshmallow_utils.fields import EDTFDateString


def to_pattern(pattern):
    pattern = pattern.replace('Y', '(?P<year>[0-9]{4})').replace('Y', '(?P<month>[0-9]{1,2})')
    return re.compile(pattern)


class StringDateField(fields.Field):
    valid_patterns = [
        to_pattern(x) for x in (
            'Y',
            'YM'
        )
    ]

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None

        for pattern in self.valid_patterns:
            match = pattern.match(value)
            if match:
                month = match.groupdict().get('month', None)
                if month:
                    if not (1 <= int(month) <= 12):
                        raise ValidationError(
                            message=_('Bad month value'),
                            field_name=attr
                        )
                return value
        try:
            from_iso_datetime(value)
            return value
        except:
            pass
        try:
            from_iso_date(value)
            return value
        except:
            pass
        raise ValidationError(
            message=_('Unsupported date string'),
            field_name=attr
        )


class DateWithdrawn(Schema):
    date = EDTFDateString()     # TODO: only date, not interval !
    dateInformation = fields.String()