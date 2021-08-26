import pytest

from nr_datasets_metadata.marshmallow.dataset import DataSetMetadataSchemaV3

from nr_datasets_metadata import marshmallow
from flask_login import LoginManager

class MD(DataSetMetadataSchemaV3):
    pass

def test_marshmallow(app, db, taxonomy_tree, new_datamodel_jschema_test, fundingReference_test):

   
    data = new_datamodel_jschema_test
    assert data == MD().load(data)

    #dates #todo range check


    # fundingReference
    data = fundingReference_test
    assert data == MD().load(data)



