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
        'affiliation': AMU,
        'role': [{'dataCiteCode': 'Supervisor',
                  'is_ancestor': False,
                  'level': 1,
                  'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/supervisor'},
                  'title': {'cs': 'supervizor',
                            'en': 'supervisor'}}]
    })


def test_whole_marshmallow(app, db, taxonomy_tree):
    assert_schema_passing(
        DataSetMetadataSchemaV3,
        {
         'abstract': {'cs': 'kchc'},
         'accessRights': [{'is_ancestor': False,
                           'level': 1,
                           'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/c-abf2'},
                           'relatedURI': {'coar': 'http://purl.org/coar/access_right/c_abf2',
                                          'eprint': 'http://purl.org/eprint/accessRights/OpenAccess',
                                          'vocabs': 'https://vocabs.acdh.oeaw.ac.at/archeaccessrestrictions/public'},
                           'title': {'cs': 'otevřený přístup', 'en': 'open access'}}],
         'contributors': [{'affiliation': [{'address': 'Malostranské náměstí 259/12, '
                                                       '118 00 Praha 1',
                                            'fullName': 'test',
                                            'ico': '61384984',
                                            'is_ancestor': False,
                                            'level': 1,
                                            'links': {
                                                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/61384984'},
                                            'nameType': 'Organizational',
                                            'provider': True,
                                            'related': {'rid': '51000'},
                                            'title': {'cs': 'Akademie múzických umění '
                                                            'v Praze',
                                                      'en': 'Academy of Performing '
                                                            'Arts in Prague'},
                                            'type': 'veřejná VŠ',
                                            'url': 'https://www.amu.cz'}],
                           'authorityIdentifiers': [{'identifier': 'jej---',
                                                     'scheme': 'orcid'}],
                           'fullName': 'Alzbeta Pokorna',
                           'nameType': 'Personal',
                           'role': [{'dataCiteCode': 'Supervisor',
                                     'is_ancestor': False,
                                     'level': 1,
                                     'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/supervisor'},
                                     'title': {'cs': 'supervizor',
                                               'en': 'supervisor'}}]}],
         'creators': [{'affiliation': [{'address': 'Malostranské náměstí 259/12, 118 '
                                                   '00 Praha 1',
                                        'fullName': 'test',
                                        'ico': '61384984',
                                        'is_ancestor': False,
                                        'level': 1,
                                        'links': {
                                            'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/61384984'},
                                        'nameType': 'Organizational',
                                        'provider': True,
                                        'related': {'rid': '51000'},
                                        'title': {'cs': 'Akademie múzických umění v '
                                                        'Praze',
                                                  'en': 'Academy of Performing Arts in '
                                                        'Prague'},
                                        'type': 'veřejná VŠ',
                                        'url': 'https://www.amu.cz'}],
                       'authorityIdentifiers': [{'identifier': 'jej---',
                                                 'scheme': 'orcid'}],
                       'fullName': 'Alzbeta Pokorna',
                       'nameType': 'Personal'}],
         'dateAvailable': '1970',
         'dateCollected': '2018-03',
         'dateCreated': '1996-10-12',
         'dateModified': '1999',
         'dateValidTo': '1996-10',
         'dateWithdrawn': {'date': '1970', 'dateInformation': 'informace'},
         'fundingReferences': [{'funder': [{'funderISVaVaICode': '123456789',
                                           'is_ancestor': False,
                                           'level': 1,
                                           'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/ntk'},
                                           'title': {'cs': 'Národní technická knihovna',
                                                     'en': 'National library of '
                                                           'technology'}}],
                               'fundingProgram': 'jeeej',
                               'projectID': 'kch',
                               'projectName': 'kk'}],
         'geoLocations': [{'geoLocationPlace': 'place',
                          'geoLocationPoint': {'pointLatitude': 0,
                                               'pointLongitude': 100}}],
         'keywords': [{'cs': 'jej', 'en': 'yey'}, {'cs': 'jejj', 'en': 'yey!'}],
         'language': [{'is_ancestor': False,
                       'level': 1,
                       'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cze'},
                       'title': {'cs': 'čeština', 'en': 'Czech'}}],
         'methods': {'en': 'method'},
         'notes': ['nota1', 'nota2'],
         'persistentIdentifiers': [{'identifier': '10.1038/nphys1170',
                                    'scheme': 'doi',
                                    'status': 'requested'}],
         'relatedItems': [{'itemContributors': [{'affiliation': [{'address': 'Malostranské '
                                                                            'náměstí '
                                                                            '259/12, '
                                                                            '118 00 '
                                                                            'Praha 1',
                                                                 'fullName': 'test',
                                                                 'ico': '61384984',
                                                                 'is_ancestor': False,
                                                                 'level': 1,
                                                                 'links': {
                                                                     'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/61384984'},
                                                                 'nameType': 'Organizational',
                                                                 'provider': True,
                                                                 'related': {'rid': '51000'},
                                                                 'title': {'cs': 'Akademie '
                                                                                 'múzických '
                                                                                 'umění '
                                                                                 'v '
                                                                                 'Praze',
                                                                           'en': 'Academy '
                                                                                 'of '
                                                                                 'Performing '
                                                                                 'Arts '
                                                                                 'in '
                                                                                 'Prague'},
                                                                 'type': 'veřejná VŠ',
                                                                 'url': 'https://www.amu.cz'}],
                                                'authorityIdentifiers': [{'identifier': 'jej---',
                                                                          'scheme': 'orcid'}],
                                                'fullName': 'Alzbeta Pokorna',
                                                'nameType': 'Personal',
                                                'role': [{'dataCiteCode': 'Supervisor',
                                                          'is_ancestor': False,
                                                          'level': 1,
                                                          'links': {
                                                              'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/supervisor'},
                                                          'title': {'cs': 'supervizor',
                                                                    'en': 'supervisor'}}]}],
                           'itemCreators': [{'affiliation': [{'address': 'Malostranské '
                                                                        'náměstí '
                                                                        '259/12, 118 '
                                                                        '00 Praha 1',
                                                             'fullName': 'test',
                                                             'ico': '61384984',
                                                             'is_ancestor': False,
                                                             'level': 1,
                                                             'links': {
                                                                 'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/61384984'},
                                                             'nameType': 'Organizational',
                                                             'provider': True,
                                                             'related': {'rid': '51000'},
                                                             'title': {'cs': 'Akademie '
                                                                             'múzických '
                                                                             'umění v '
                                                                             'Praze',
                                                                       'en': 'Academy '
                                                                             'of '
                                                                             'Performing '
                                                                             'Arts in '
                                                                             'Prague'},
                                                             'type': 'veřejná VŠ',
                                                             'url': 'https://www.amu.cz'}],
                                            'authorityIdentifiers': [{'identifier': 'jej---',
                                                                      'scheme': 'orcid'}],
                                            'fullName': 'Alzbeta Pokorna',
                                            'nameType': 'Personal'}],
                           'itemEndPage': 'konec',
                           'itemIssue': 'issue',
                           'itemPIDs': [{'identifier': '10.1038/nphys1170',
                                         'scheme': 'doi'}],
                           'itemPublisher': 'publisher',
                           'itemRelationType': [{'is_ancestor': False,
                                                 'level': 1,
                                                 'links': {
                                                     'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/article'},
                                                 'title': {'cs': 'Article'}}],
                           'itemResourceType': [{'is_ancestor': False,
                                                 'level': 1,
                                                 'links': {
                                                     'self': 'http://127.0.0.1:5000/2.0/taxonomies/resourceType/datasets'},
                                                 'title': {'cs': 'Datasety'}}],
                           'itemStartPage': 'start',
                           'itemTitle': 'titulek',
                           'itemVolume': 'volume',
                           'itemYear': '1970'}],
         'resourceType': [{'is_ancestor': False,
                           'level': 1,
                           'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/resourceType/datasets'},
                           'title': {'cs': 'Datasety'}}],
         'rights': [{'is_ancestor': False,
                     'level': 1,
                     'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/licenses/cc'},
                     'title': {'cs': 'Licence Creative Commons'}}],
        'publisher' : [{'is_ancestor': False,
                     'level': 1,
                     'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/licenses/cc'},
                     'title': {'cs': 'Licence Creative Commons'}},
                       {'funderISVaVaICode': '123456789',
                        'is_ancestor': False,
                        'level': 1,
                        'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/ntk'},
                        'title': {'cs': 'Národní technická knihovna',
                                  'en': 'National library of '
                                        'technology'}}
                       ],
         'subjectCategories': [{'DateRevised': '2007-01-26T16:14:37',
                                'is_ancestor': False,
                                'level': 1,
                                'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/psh3001'},
                                'relatedURI': [],
                                'title': {'cs': 'Reynoldsovo číslo',
                                          'en': 'Reynolds number'}}],
         'technicalInfo': {'cs': 'das TechnicalInfo'},
         'titles': [{'title': {'cs': 'jeej'}, 'titleType': 'mainTitle'},
                    {'title': {'cs': 'jeej'}, 'titleType': 'subtitle'}],
         'version': 'jeeej'
         }
    )
