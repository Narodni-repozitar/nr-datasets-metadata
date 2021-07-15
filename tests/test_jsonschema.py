from invenio_jsonschemas import current_jsonschemas

from nr_datasets_metadata.record import DatasetBaseRecord


def test_json(app, db, taxonomy_tree, base_json):
    print("\n\n\n\n\n")
    print("START")
    print(app)
    print(current_jsonschemas.list_schemas())
    DatasetBaseRecord(base_json).validate()
