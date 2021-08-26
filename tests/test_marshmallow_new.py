from nr_datasets_metadata.marshmallow.dataset import DataSetMetadataSchemaV3

from nr_datasets_metadata import marshmallow
from flask_login import LoginManager

class MD(DataSetMetadataSchemaV3):
    pass

def test_marshmallow(app):
    LoginManager(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    #base
    data = {"titles": [{"title": {"cs": "jej"}, "title_type": "mainTitle"}]}
    assert data == MD().load(data)
    #titles
    data = {"titles": [{"title" :{"cs": "jej"}, "title_type": "mainTitle"}, {"title" :{"cs": "jej"}, "title_type": "subtitle"}]}
    assert data == MD().load(data)
    #resourceType
    data = {"titles": [{"title": {"cs": "jej"}, "title_type": "mainTitle"}], "resourceType": [{'links': {'self': 'http://localhost/2.0/taxonomies/licenses/copyright'}}]}
    assert data == MD().load(data)