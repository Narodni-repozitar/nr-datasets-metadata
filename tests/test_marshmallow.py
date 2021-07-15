import pytest
from marshmallow import ValidationError

from nr_datasets_metadata.marshmallow import DatasetMetadataSchemaV1


def test_required_fields(app, db, taxonomy_tree, base_json, base_json_dereferenced):
    schema = DatasetMetadataSchemaV1()
    json = base_json
    result = schema.load(json)
    assert result == base_json_dereferenced
