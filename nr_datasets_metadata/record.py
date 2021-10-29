from invenio_records.api import Record
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin

from .constants import DATASETS_ALLOWED_SCHEMAS, DATASETS_PREFERRED_SCHEMA
from .marshmallow import DataSetMetadataSchemaV3
from oarepo_invenio_model import InheritedSchemaRecordMixin


DATE_RANGE_FIELDS = ['dateCreated', 'dateCollected']


# TODO: this needs to be made more generic before we can support more schemas
def date_ranges_to_index(sender, json=None, record=None,
                         index=None, doc_type=None, arguments=None, **kwargs):

    for dr in DATE_RANGE_FIELDS:
        if dr in json:
            dates = json[dr].split('/', 1)
            if len(dates) == 1:
                since = until = dates[0]
            else:
                since, until = dates

            json[f"{dr}Range"] = {
                'gte': since,
                'lte': until
            }

    return json


class DatasetBaseRecord(SchemaKeepingRecordMixin,
                        MarshmallowValidatedRecordMixin,
                        InheritedSchemaRecordMixin,
                        Record):
    ALLOWED_SCHEMAS = DATASETS_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = DATASETS_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = DataSetMetadataSchemaV3
