from invenio_records.api import Record
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin

from .constants import DATASETS_ALLOWED_SCHEMAS, DATASETS_PREFERRED_SCHEMA
from .marshmallow import DatasetMetadataSchemaV1
from oarepo_invenio_model import InheritedSchemaRecordMixin


class DatasetBaseRecord(SchemaKeepingRecordMixin,
                        MarshmallowValidatedRecordMixin,
                        InheritedSchemaRecordMixin,
                        Record):
    ALLOWED_SCHEMAS = DATASETS_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = DATASETS_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = DatasetMetadataSchemaV1
