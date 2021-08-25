from nr_datasets_metadata.marshmallow.dataset import DataSetMetadataSchemaV2

from nr_datasets_metadata import marshmallow

class MD(DataSetMetadataSchemaV2):
    pass

def test_withoutApp():


    data = {"titles": [{"title" :{"cs": "jej"}, "title_type": "mainTitle"}, {"title" :{"cs": "jej"}, "title_type": "mainTitle"}]}

    assert data == MD().load(data)