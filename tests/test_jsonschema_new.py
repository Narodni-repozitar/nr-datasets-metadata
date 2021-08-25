import json
import pathlib

import jsonschema
from jsonschema import validate
from oarepo_invenio_model import AllOfDraft7Validator


def get_schema():
    """This function loads the given schema available"""

    try:
        with open('test_module/jsonschemas/test/test-v1.0.0.json', 'r') as file:
            schema = json.load(file)
    except:
        with open('./tests/test_module/jsonschemas/test/test-v1.0.0.json', 'r') as file:
            schema = json.load(file)

    return schema
def test_json(app):
    """Test of json schema with app."""
    # resolve = jsonschema.RefResolver('https://narodni-repozitar.cz/',get_schema())
    # data = json.loads('{"these": {"titles" : []}}')
    # validate(instance=data, schema=get_schema(), resolver=resolve)
    schema = app.extensions['invenio-records']
    #nutne minimum
    data = json.loads('{"these": '
                      '{'
                      '"$schema":"https://narodni-repozitar.cz/schemas/nr_datasets_metadata/nr-datasets-metadata-v2.0.0.json",'
                      '"InvenioID": "1",'
                      '"titles" : [{"title": {"cs" : "jeej"}, "titleType": "mainTitle"}], '
                      '"creator" : ['
                            '{"nameType": "Personal", '
                            '"affiliaton": [{"termin": "termin"}], '
                            '"fullName": "Alzbeta Pokorna", '
                            '"authorityIdentifiers": [{"identifier": "jej", "scheme": "ORCID"}]'
                            '}'
                        '],'
                      '"dateAvailable": "1970",'
                      '"resourceType": [{"termin": "termin"}],'
                      '"accessRights" : [{"termin": "termin"}],'
                      '"abstract" : {"cs": "kchc"},'
                      '"subjectCategory": [{"termin": "termin"}] '
                      '}'
                      '}')
    #data = json.loads('{"these": {"titles" : [{"title" :{"cs": "jej", "en": "yay"}, "titleType": "mainTitle"}]}}')
    schema.validate(data, get_schema(), cls=AllOfDraft7Validator)

    # data = json.loads('{"these": {"abstract" : {"cs": "jej", "en": "yay"}, "contributor" : "Alzbeta Pokorna", "modified":"2012-04-23T18:25:43.511Z"}}')
    # schema.validate(data, get_schema())

    # data = json.loads('{"these": {"abstract" : 1}}')
    # with pytest.raises(ValidationError):
    #     schema.validate(data, get_schema())
    #
    # data = json.loads('{"these": {"abstract" : {"css": "jej", "en": "yay"}}}')
    # with pytest.raises(ValidationError):
    #     schema.validate(data, get_schema())