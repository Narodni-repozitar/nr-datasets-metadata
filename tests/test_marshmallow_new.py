import pytest

from nr_datasets_metadata.marshmallow.dataset import DataSetMetadataSchemaV3

from nr_datasets_metadata import marshmallow
from flask_login import LoginManager

class MD(DataSetMetadataSchemaV3):
    pass

def test_marshmallow(app, db, taxonomy_tree, tax_test, fundingReference_test):

    #base
    data = {"InvenioID": "xx","titles": [{"title": {"cs": "jej"}, "title_type": "mainTitle"}]}
    assert data == MD().load(data)

    #titles
    data = {"persistentIdentifiers" : [{"identifier": "10.5281/zenodo.5257698", "scheme": "doi", "status" : "requested"}],"titles": [{"title" :{"cs": "jej"}, "title_type": "mainTitle"}, {"title" :{"cs": "jej"}, "title_type": "subtitle"}]}
    assert data == MD().load(data)

    #resourceType
    data = tax_test
    assert data == MD().load(data)

    #dates #todo range check
    data = {"titles": [{"title": {"cs": "jej"}, "title_type": "mainTitle"}], "dateAvailable": "1970", "dateModified": "1990",
            "dateCollected": "1970", "dateValidTo": "1990", "dateWithdrawn": {"date": "1998", "dateInformation" : "kch"}}
    assert data == MD().load(data)

    # multilinguals
    data = {"titles": [{"title": {"cs": "jej"}, "title_type": "mainTitle"}], "keywords": {"cs" : "test"},
            "abstract" : {"cs" : "test"},
            "methods": {"cs" : "test"},
            "version" : "kch",
            "technicalInfo" : {"cs" : "test"}}
    assert data == MD().load(data)

    # geo
    data = {"titles": [{"title": {"cs": "jej"}, "title_type": "mainTitle"}], "keywords": {"cs": "test"},
            "geoLocation": [{"geoLocationPlace": "place","geoLocationPoint": { "pointLongitude": 100, "pointLatitude": 0} }] }
    assert data == MD().load(data)

    # fundingReference
    data = fundingReference_test
    assert data == MD().load(data)



