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

    schema = app.extensions['invenio-records']

    # bare minimum
    data = {"these":
        {
            "InvenioID": "1",
            "titles": [{"title": {"cs": "jeej"}, "titleType": "mainTitle"}],
            "creators": [
                {"nameType": "Personal",
                 "affiliatoin": [{"termin": "termin"}],
                 "fullName": "Alzbeta Pokorna",
                 "authorityIdentifiers": [{"identifier": "jej", "scheme": "orcid"}]
                 }
            ],
            "dateAvailable": "1970",
            "resourceType": [{"termin": "termin"}],
            "accessRights": [{"termin": "termin"}],
            "abstract": {"cs": "kchc"},
            "subjectCategories": [{"termin": "termin"}]
        }
    }

    schema.validate(data, get_schema(), cls=AllOfDraft7Validator)

    # organization todo
    data = {"these":
        {
            "InvenioID": "1",
            "titles": [{"title": {"cs": "jeej"}, "titleType": "mainTitle"}],
            "creators": [
                {"nameType": "Personal",
                 "affiliation": [{"termin": "termin"}],
                 "fullName": "Alzbeta Pokorna",
                 "authorityIdentifiers": [{"identifier": "jej", "scheme": "orcid"}]
                 }
            ],
            "dateAvailable": "1970",
            "resourceType": [{"termin": "termin"}],
            "accessRights": [{"termin": "termin"}],
            "abstract": {"cs": "kchc"},
            "subjectCategories": [{"termin": "termin"}]
        }
    }

    schema.validate(data, get_schema(), cls=AllOfDraft7Validator)

    # all properties used
    data = {"these":
        {
            "InvenioID": "1",
            "titles": [{"title": {"cs": "jeej"}, "titleType": "mainTitle"},
                       {"title": {"cs": "jeej"}, "titleType": "subtitle"}],
            "creators": [
                {"nameType": "Personal",
                 "affiliaton": [{"termin": "termin"}],
                 "fullName": "Alzbeta Pokorna",
                 "authorityIdentifiers": [{"identifier": "jej", "scheme": "orcid"}]
                 }
            ],
            "contributors": [
                {"nameType": "Personal",
                 "affiliaton": [{"termin": "termin"}],
                 "fullName": "Alzbeta Pokorna",
                 "role": [{"termin": "termin"}],
                 "authorityIdentifiers": [{"identifier": "jej", "scheme": "orcid"}]
                 }
            ],
            "dateAvailable": "1970",
            "resourceType": [{"termin": "termin"}],
            "accessRights": [{"termin": "termin"}],
            "abstract": {"cs": "kchc"},
            "subjectCategories": [{"termin": "termin"}],
            "dateModified": "1999",
            "dateCollected": "2018-03",
            "dateCreated": "1996-10-12",
            "dateValidTo": "xxxxxxxxxx",  # todo: json nevaliduje, marshmallow
            "dateWithdrawn": {"date": "1970", "dateInformation": "informace"},
            "keywords": [{"cs": "jej", "en-us": "yey"}, {"cs": "jejj", "en-us": "yey!"}],
            "language": [{"termin": "termin"}],
            "notes": ["nota1", "nota2"],
            "methods": {"en": "method"},
            "technicalInfo": {"de": "das TechnicalInfo"},
            "rights": [{"termin": "termin"}],
            "relatedItems":
                [{
                    "itemTitle": "titulek",
                    "itemCreators": [
                        {"nameType": "Personal",
                         "affiliaton": [{"termin": "termin"}],
                         "fullName": "Alzbeta Pokorna",
                         "authorityIdentifiers": [{"identifier": "jej", "scheme": "orcid"}]
                         }
                    ],
                    "itemContributors": [
                        {"nameType": "Personal",
                         "affiliaton": [{"termin": "termin"}],
                         "fullName": "Alzbeta Pokorna",
                         "role": [{"termin": "termin"}],
                         "authorityIdentifiers": [{"identifier": "jej", "scheme": "orcid"}]
                         }
                    ],
                    "itemPIDs": [{"identifier": "jej", "scheme": "DOI"}],
                    "itemYear": "1970",
                    "itemVolume": "volume",
                    "itemIssue": "issue",
                    "itemStartPage": "start",
                    "itemEndPage": "konec",
                    "itemPublisher": "publisher",
                    "itemRelationType": [{"termin": "termin"}],
                    "itemResourceType": [{"termin": "termin"}]
                }],
            "fundingReferences": [
                {"projectID": "kch", "projectName": "kk", "fundingProgram": "jeeej", "funder": [{"termin": "termin"}]}],
            "version": "jeeej",
            "geoLocations": [{
                "geoLocationPlace": "place",
                "geoLocationPoint": {"pointLongitude": 100, "pointLatitude": 0}
            }],
            "persistentIdentifiers": [{"identifier": "jej", "scheme": "DOI", "status": "requested"}],
        }
    }
    schema.validate(data, get_schema(), cls=AllOfDraft7Validator)
    # todo:unique items
    # todo: organization

    # data = json.loads('{"these": {"abstract" : 1}}')
    # with pytest.raises(ValidationError):
    #     schema.validate(data, get_schema())
    #
    # data = json.loads('{"these": {"abstract" : {"css": "jej", "en": "yay"}}}')
    # with pytest.raises(ValidationError):
    #     schema.validate(data, get_schema())
