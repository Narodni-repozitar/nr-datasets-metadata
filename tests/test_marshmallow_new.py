import pytest
from marshmallow import Schema, ValidationError

from nr_datasets_metadata.marshmallow import DataSetMetadataSchemaV3

from nr_datasets_metadata.marshmallow.subschemas.authority import AuthorityBaseSchema, PersonSchema, OrganizationSchema, \
    AuthoritySchema
from nr_datasets_metadata.marshmallow.subschemas.date import StringDateField
from nr_datasets_metadata.marshmallow.subschemas.geo import GeoLocationSchema
from nr_datasets_metadata.marshmallow.subschemas.person import CreatorSchema, ContributorSchema

AMU = [
    {
        'address': 'Malostranské náměstí 259/12, 118 00 Praha 1',
        'fullName': 'test',
        'ico': '61384984',
        'is_ancestor': False,
        'level': 1,
        'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/61384984'},
        'nameType': 'Organizational',
        'provider': True,
        'related': {'rid': '51000'},
        'title': {'cs': 'Akademie múzických umění v Praze',
                  'en': 'Academy of Performing Arts in Prague'},
        'type': 'veřejná VŠ',
        'url': 'https://www.amu.cz'
    }
]


def assert_schema_passing(schema_or_field, value):
    if issubclass(schema_or_field, Schema):
        s = schema_or_field()
        assert s.load(value) == value
    else:
        schema = type('Schema', (Schema,), dict(
            fld=schema_or_field()
        ))()
        assert schema.load({'fld': value}) == {'fld': value}


def assert_schema_not_passing(schema_or_field, value):
    try:
        if issubclass(schema_or_field, Schema):
            s = schema_or_field()
            s.load(value)
        else:
            schema = type('Schema', (Schema,), dict(
                fld=schema_or_field()
            ))()
            schema.load({'fld': value})
        raise Exception('Schema should not pass')
    except ValidationError:
        pass


def test_authority(app, db, taxonomy_tree):
    assert_schema_passing(
        AuthorityBaseSchema,
        {
            'fullName': 'test',
            'nameType': 'Personal',
            'authorityIdentifiers': [
                {
                    'scheme': 'orcid',
                    'identifier': '0000-0002-1825-0097'
                }
            ]
        }
    )
    assert_schema_passing(
        AuthorityBaseSchema,
        {
            'fullName': 'test',
            'nameType': 'Personal',
            'authorityIdentifiers': [
            ]
        }
    )
    assert_schema_passing(
        AuthorityBaseSchema,
        {
            'fullName': 'test',
            'nameType': 'Personal',
        }
    )


def test_person(app, db, taxonomy_tree):
    assert_schema_passing(
        PersonSchema,
        {
            'fullName': 'test',
            'nameType': 'Personal',
            'authorityIdentifiers': [
                {
                    'scheme': 'orcid',
                    'identifier': '0000-0002-1825-0097'
                }
            ]
        }
    )
    assert_schema_passing(
        PersonSchema,
        {
            'fullName': 'test',
            'nameType': 'Personal',
            'authorityIdentifiers': [
                {
                    'scheme': 'orcid',
                    'identifier': '0000-0002-1825-0097'
                }
            ],
            'affiliation': AMU
        }
    )


def test_organization(app, db, taxonomy_tree):
    assert_schema_passing(
        OrganizationSchema,
        [{
            'authorityIdentifiers': [
                {
                    'scheme': 'orcid',
                    'identifier': '0000-0002-1825-0097'
                }
            ],
            'address': 'Malostranské náměstí 259/12, 118 00 Praha 1',
            'fullName': 'test',
            'ico': '61384984',
            'is_ancestor': False,
            'level': 1,
            'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/61384984'},
            'nameType': 'Organizational',
            'provider': True,
            'related': {'rid': '51000'},
            'title': {'cs': 'Akademie múzických umění v Praze',
                      'en': 'Academy of Performing Arts in Prague'},
            'type': 'veřejná VŠ',
            'url': 'https://www.amu.cz'
        }]
    )


def test_authority_schema(app, db, taxonomy_tree):
    assert_schema_passing(
        AuthoritySchema,
        {
            'fullName': 'test',
            'nameType': 'Personal',
            'authorityIdentifiers': [
                {
                    'scheme': 'orcid',
                    'identifier': '0000-0002-1825-0097'
                }
            ],
            'affiliation': AMU
        }
    )
    assert_schema_passing(
        AuthoritySchema,
        [{
            'authorityIdentifiers': [
                {
                    'scheme': 'orcid',
                    'identifier': '0000-0002-1825-0097'
                }
            ],
            'address': 'Malostranské náměstí 259/12, 118 00 Praha 1',
            'fullName': 'test',
            'ico': '61384984',
            'is_ancestor': False,
            'level': 1,
            'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/61384984'},
            'nameType': 'Organizational',
            'provider': True,
            'related': {'rid': '51000'},
            'title': {'cs': 'Akademie múzických umění v Praze',
                      'en': 'Academy of Performing Arts in Prague'},
            'type': 'veřejná VŠ',
            'url': 'https://www.amu.cz'
        }]
    )


def test_date(app, db, taxonomy_tree):
    assert_schema_passing(StringDateField, '2021')
    assert_schema_passing(StringDateField, '202102')
    assert_schema_passing(StringDateField, '2021-02-01')
    assert_schema_passing(StringDateField, '2021-02-01T00:01:00+0200')


def test_geo(app, db):
    assert_schema_passing(GeoLocationSchema, {
        'geoLocationPlace': 'Prague'
    })
    assert_schema_passing(GeoLocationSchema, {
        'geoLocationPlace': 'Prague',
        'geoLocationPoint': {
            'pointLatitude': 51,
            'pointLongitude': 21,
        }
    })


def test_creator(app, db, taxonomy_tree):
    assert_schema_not_passing(CreatorSchema, {
        'fullName': 'test',
        'nameType': 'Personal',
        'authorityIdentifiers': [
            {
                'scheme': 'orcid',
                'identifier': '0000-0002-1825-0097'
            }
        ]
    })

    assert_schema_passing(CreatorSchema, {
        'fullName': 'test',
        'nameType': 'Personal',
        'authorityIdentifiers': [
            {
                'scheme': 'orcid',
                'identifier': '0000-0002-1825-0097'
            }
        ],
        'affiliation': AMU
    })


def test_contributor(app, db, taxonomy_tree):
    assert_schema_not_passing(ContributorSchema, {
        'fullName': 'test',
        'nameType': 'Personal',
        'authorityIdentifiers': [
            {
                'scheme': 'orcid',
                'identifier': '0000-0002-1825-0097'
            }
        ]
    })

    assert_schema_passing(ContributorSchema, {
        'fullName': 'test',
        'nameType': 'Personal',
        'authorityIdentifiers': [
            {
                'scheme': 'orcid',
                'identifier': '0000-0002-1825-0097'
            }
        ],
        'affiliation': AMU
    })


def test_whole_marshmallow(app, db, taxonomy_tree):
    assert_schema_passing(DataSetMetadataSchemaV3, {
        "InvenioID": "1",
        "titles": [{"title": {"cs": "jeej"}, "titleType": "mainTitle"},
                   {"title": {"cs": "jeej"}, "titleType": "subtitle"}],
        "creators": [
            {"nameType": "Personal",
             "affiliation": AMU,
             "fullName": "Alzbeta Pokorna",
             "authorityIdentifiers": [{"identifier": "jej", "scheme": "orcid"}]
             }
        ],
        "contributors": [
            {"nameType": "Personal",
             "affiliation": AMU,
             "fullName": "Alzbeta Pokorna",
             "role": [{"links": {"self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/supervisor"}}],
             "authorityIdentifiers": [{"identifier": "jej", "scheme": "orcid"}]
             }
        ],
        "dateAvailable": "1970",
        "resourceType": [{"links": {"self": "http://127.0.0.1:5000/2.0/taxonomies/resourceType/datasets"}}],
        "accessRights": [{"title": {
            "cs": "otevřený přístup",
            "en": "open access"
        },
            "relatedURI": {
                "coar": "http://purl.org/coar/access_right/c_abf2",
                "vocabs": "https://vocabs.acdh.oeaw.ac.at/archeaccessrestrictions/public",
                "eprint": "http://purl.org/eprint/accessRights/OpenAccess"
            }, "links": {"self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/c-abf2"}}],
        "abstract": {"cs": "kchc"},
        "subjectCategories": [{"links": {"self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/psh3001"}}],
        "dateModified": "1999",
        "dateCollected": "2018-03",
        "dateCreated": "1996-10-12",
        "dateValidTo": "1996-10",
        "dateWithdrawn": {"date": "1970", "dateInformation": "informace"},
        "keywords": [{"cs": "jej", "en": "yey"}, {"cs": "jejj", "en": "yey!"}],
        "language": [{"links": {"self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cze"}}],
        "note": ["nota1", "nota2"],
        "methods": {"en": "method"},
        "technicalInfo": {"cs": "das TechnicalInfo"},
        "rights": [{"links": {"self": "http://127.0.0.1:5000/2.0/taxonomies/licenses/cc"}}],
        "relatedItems":
            [{
                "itemTitle": "titulek",
                "itemCreator": [
                    {"nameType": "Personal",
                     'affiliation': AMU,
                     "fullName": "Alzbeta Pokorna",
                     "authorityIdentifiers": [{"identifier": "jej", "scheme": "orcid"}]
                     }
                ],
                "itemContributor": [
                    {"nameType": "Personal",
                     'affiliation': AMU,
                     "fullName": "Alzbeta Pokorna",
                     "role": [{"termin": "termin"}],
                     "authorityIdentifiers": [{"identifier": "jej", "scheme": "orcid"}]
                     }
                ],
                "itemPIDs": [{"identifier": "10.1038/nphys1170", "scheme": "doi"}],
                "itemYear": "1970",
                "itemVolume": "volume",
                "itemIssue": "issue",
                "itemStartPage": "start",
                "itemEndPage": "konec",
                "itemPublisher": "publisher",
                "itemRelationType": [{"links": {"self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/article"}}],
                "itemResourceType": [{"links": {"self": "http://127.0.0.1:5000/2.0/taxonomies/resourceType/datasets"}}]
            }],
        "fundingReference": [
            {"projectID": "kch", "projectName": "kk", "fundingProgram": "jeeej",
             "funder": [{"links": {"self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/ntk"}}]}],
        "version": "jeeej",
        "geoLocation": [{
            "geoLocationPlace": "place",
            "geoLocationPoint": {"pointLongitude": 100, "pointLatitude": 0}
        }],
        "persistentIdentifiers": [{"identifier": "jej", "scheme": "DOI", "status": "requested"}],
    })
