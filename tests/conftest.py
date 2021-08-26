from __future__ import absolute_import, print_function

import os
import pytest
import shutil
import subprocess
import sys
import tempfile
import uuid
from elasticsearch import Elasticsearch
from flask import Flask, make_response, url_for
from flask_login import LoginManager, login_user
from flask_principal import RoleNeed, Principal, Permission
from flask_taxonomies.proxies import current_flask_taxonomies
from flask_taxonomies.term_identification import TermIdentification
from invenio_access import InvenioAccess
from invenio_accounts import InvenioAccounts
from invenio_accounts.models import User
from invenio_base.signals import app_loaded
from invenio_celery import InvenioCelery
from invenio_db import InvenioDB
from invenio_db import db as db_
from invenio_indexer import InvenioIndexer
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_pidstore import InvenioPIDStore
from invenio_pidstore.providers.recordid import RecordIdProvider
from invenio_records import InvenioRecords, Record
from invenio_records_rest import InvenioRecordsREST
from invenio_records_rest.schemas.fields import SanitizedUnicode
from invenio_records_rest.utils import PIDConverter
from invenio_records_rest.views import create_blueprint_from_app
from invenio_search import InvenioSearch, RecordsSearch
from marshmallow import Schema
from marshmallow.fields import Url, Boolean, Nested, List
from oarepo_mapping_includes.ext import OARepoMappingIncludesExt
from oarepo_references import OARepoReferences
from oarepo_references.mixins import ReferenceEnabledRecordMixin
from oarepo_taxonomies.cli import init_db, import_taxonomy
from oarepo_taxonomies.ext import OarepoTaxonomies
from oarepo_validate import MarshmallowValidatedRecordMixin
from oarepo_validate.ext import OARepoValidate
from pathlib import Path
from sqlalchemy_utils import database_exists, create_database, drop_database

from tests.helpers import set_identity


class Links(Schema):
    self = Url()


class ResourceType(Schema):
    is_ancestor = Boolean()
    links = Nested(Links)


class TestSchema(Schema):
    """Test record schema."""
    title = SanitizedUnicode()
    control_number = SanitizedUnicode()
    resourceType = List(Nested(ResourceType))


class TestRecord(MarshmallowValidatedRecordMixin,
                 ReferenceEnabledRecordMixin,
                 Record):
    """Reference enabled test record class."""
    MARSHMALLOW_SCHEMA = TestSchema
    VALIDATE_MARSHMALLOW = True
    VALIDATE_PATCH = True

    @property
    def canonical_url(self):
        # SERVER_NAME = current_app.config["SERVER_NAME"]
        # return f"https://{SERVER_NAME}/api/records/{self['pid']}"
        return url_for('invenio_records_rest.recid_item',
                       pid_value=self['pid'], _external=True)


RECORDS_REST_ENDPOINTS = {
    'recid': dict(
        pid_type='nr',
        pid_minter='nr',
        pid_fetcher='nr',
        default_endpoint_prefix=True,
        search_class=RecordsSearch,
        indexer_class=RecordIndexer,
        search_index='records',
        search_type=None,
        record_serializers={
            'application/json': 'oarepo_validate:json_response',
        },
        search_serializers={
            'application/json': 'oarepo_validate:json_search',
        },
        record_loaders={
            'application/json': 'oarepo_validate:json_loader',
        },
        record_class=TestRecord,
        list_route='/records/',
        item_route='/records/<pid(nr):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        error_handlers=dict()
    )
}


@pytest.yield_fixture(scope="module")
def app():
    instance_path = tempfile.mkdtemp()
    app = Flask('testapp', instance_path=instance_path)

    app.config.update(
        JSONSCHEMAS_HOST="narodni-repozitar.cz",
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        SERVER_NAME='127.0.0.1:5000',
        INVENIO_INSTANCE_PATH=instance_path,
        DEBUG=True,
        # in tests, api is not on /api but directly in the root
        PIDSTORE_RECID_FIELD='pid',
        FLASK_TAXONOMIES_URL_PREFIX='/2.0/taxonomies/',
        # RECORDS_REST_ENDPOINTS=RECORDS_REST_ENDPOINTS,
        CELERY_BROKER_URL='amqp://guest:guest@localhost:5672//',
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_TASK_EAGER_PROPAGATES=True,
        SUPPORTED_LANGUAGES=["cs", "en"],
        # RECORDS_REST_ENDPOINTS=RECORDS_REST_ENDPOINTS,
        ELASTICSEARCH_DEFAULT_LANGUAGE_TEMPLATE={
            "type": "text",
            "fields": {
                "keywords": {
                    "type": "keyword"
                }
            }
        },
        OAREPO_COMMUNITIES_ENDPOINTS=[]
    )

    app.secret_key = 'changeme'
    print(os.environ.get("INVENIO_INSTANCE_PATH"))

    InvenioDB(app)
    OarepoTaxonomies(app)
    OARepoReferences(app)
    InvenioAccounts(app)
    InvenioAccess(app)
    Principal(app)
    InvenioJSONSchemas(app)
    InvenioSearch(app)
    InvenioIndexer(app)
    OARepoMappingIncludesExt(app)
    InvenioRecords(app)
    InvenioRecordsREST(app)
    InvenioCelery(app)
    InvenioPIDStore(app)
    OARepoValidate(app)
    app.url_map.converters['pid'] = PIDConverter

    # Celery
    print(app.config["CELERY_BROKER_URL"])

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def basic_user_loader(user_id):
        user_obj = User.query.get(int(user_id))
        return user_obj

    app.register_blueprint(create_blueprint_from_app(app))

    @app.route('/test/login/<int:id>', methods=['GET', 'POST'])
    def test_login(id):
        print("test: logging user with id", id)
        response = make_response()
        user = User.query.get(id)
        login_user(user)
        set_identity(user)
        return response

    # app.extensions['invenio-search'].mappings["test"] = mapping
    # app.extensions["invenio-jsonschemas"].schemas["test"] = schema

    app_loaded.send(app, app=app)

    with app.app_context():
        # app.register_blueprint(taxonomies_blueprint)
        print(app.url_map)
        yield app

    shutil.rmtree(instance_path)


@pytest.fixture(scope="module")
def db(app):
    """Create database for the tests."""
    dir_path = os.path.dirname(__file__)
    parent_path = str(Path(dir_path).parent)
    db_path = os.environ.get('SQLALCHEMY_DATABASE_URI', f'sqlite:////{parent_path}/database.db')
    os.environ["INVENIO_SQLALCHEMY_DATABASE_URI"] = db_path
    app.config.update(
        SQLALCHEMY_DATABASE_URI=db_path
    )
    if database_exists(str(db_.engine.url)):
        drop_database(db_.engine.url)
    if not database_exists(str(db_.engine.url)):
        create_database(db_.engine.url)
    db_.create_all()
    #subprocess.run(["invenio", "taxonomies", "init"])
    runner = app.test_cli_runner()
    result = runner.invoke(init_db)
    if result.exit_code:
        print(result.output, file=sys.stderr)
    assert result.exit_code == 0
    for f in os.listdir('taxonomies'):
        result = runner.invoke(import_taxonomy, os.path.join('taxonomies', f))
        if result.exit_code:
            print(result.output, file=sys.stderr)
        assert result.exit_code == 0
    yield db_

    # Explicitly close DB connection
    db_.session.close()
    db_.drop_all()
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client(app, db):
    from flask_taxonomies.models import Base
    Base.metadata.create_all(db.engine)
    return app.test_client()


@pytest.fixture()
def es():
    return Elasticsearch()


@pytest.yield_fixture
def es_index(es):
    index_name = "test_index"
    if not es.indices.exists(index=index_name):
        yield es.indices.create(index_name)

    if es.indices.exists(index=index_name):
        es.indices.delete(index_name)


@pytest.fixture
def permission_client(app, db):
    app.config.update(
        FLASK_TAXONOMIES_PERMISSION_FACTORIES={
            'taxonomy_create': [Permission(RoleNeed('admin'))],
            'taxonomy_update': [Permission(RoleNeed('admin'))],
            'taxonomy_delete': [Permission(RoleNeed('admin'))],

            'taxonomy_term_create': [Permission(RoleNeed('admin'))],
            'taxonomy_term_update': [Permission(RoleNeed('admin'))],
            'taxonomy_term_delete': [Permission(RoleNeed('admin'))],
            'taxonomy_term_move': [Permission(RoleNeed('admin'))],
        }
    )
    from flask_taxonomies.models import Base
    Base.metadata.create_all(db.engine)
    return app.test_client()


@pytest.fixture
def tax_url(app):
    url = app.config['FLASK_TAXONOMIES_URL_PREFIX']
    if not url.endswith('/'):
        url += '/'
    return url


@pytest.fixture(scope="module")
def taxonomy(app, db):
    taxonomy = current_flask_taxonomies.create_taxonomy("test_taxonomy", extra_data={
        "title":
            {
                "cs": "test_taxonomy",
                "en": "test_taxonomy"
            }
    })
    db.session.commit()
    return taxonomy


@pytest.fixture(scope="module")
def taxonomy_tree(app, db, taxonomy):
    # accessRights
    id1 = TermIdentification(taxonomy=taxonomy, slug="c_abf2")
    term1 = current_flask_taxonomies.create_term(id1, extra_data={
        "title": {
            "cs": "otevřený přístup",
            "en": "open access"
        },
        "relatedURI": {
            "coar": "http://purl.org/coar/access_right/c_abf2",
            "vocabs": "https://vocabs.acdh.oeaw.ac.at/archeaccessrestrictions/public",
            "eprint": "http://purl.org/eprint/accessRights/OpenAccess"
        }
    })

    # resource type
    id2 = TermIdentification(taxonomy=taxonomy, slug="bakalarske_prace")
    term2 = current_flask_taxonomies.create_term(id2, extra_data={
        "title": {
            "cs": "Bakalářské práce",
            "en": "Bachelor’s theses"
        }
    })

    # institution
    id3 = TermIdentification(taxonomy=taxonomy, slug="61384984")
    term3 = current_flask_taxonomies.create_term(id3, extra_data={
        "title": {
            "cs": "Akademie múzických umění v Praze",
            "en": "Academy of Performing Arts in Prague"
        },
        "type": "veřejná VŠ",
        "aliases": ["AMU"],
        "related": {
            "rid": "51000"
        },
        "address": "Malostranské náměstí 259/12, 118 00 Praha 1",
        "ico": "61384984",
        "url": "https://www.amu.cz",
        "provider": True,
    })

    # language
    id4 = TermIdentification(taxonomy=taxonomy, slug="cze")
    term4 = current_flask_taxonomies.create_term(id4, extra_data={
        "title": {
            "cs": "čeština",
            "en": "Czech"
        }
    })

    # contributor
    id5 = TermIdentification(taxonomy=taxonomy, slug="supervisor")
    term5 = current_flask_taxonomies.create_term(id5, extra_data={
        "title": {
            "cs": "supervizor",
            "en": "supervisor"
        },
        "dataCiteCode": "Supervisor"
    })

    # funder
    id6 = TermIdentification(taxonomy=taxonomy, slug="ntk")
    term6 = current_flask_taxonomies.create_term(id6, extra_data={
        "title": {
            "cs": "Národní technická knihovna",
            "en": "National library of technology"
        },
        "funderISVaVaICode": "123456789"
    })

    # country
    id7 = TermIdentification(taxonomy=taxonomy, slug="cz")
    term7 = current_flask_taxonomies.create_term(id7, extra_data={
        "title": {
            "cs": "Česko",
            "en": "Czechia"
        },
        "code": {
            "number": "203",
            "alpha2": "CZ",
            "alpha3": "CZE"
        }
    })

    # relationship
    id8 = TermIdentification(taxonomy=taxonomy, slug="isversionof")
    term8 = current_flask_taxonomies.create_term(id8, extra_data={
        "title": {
            "cs": "jeVerzí",
            "en": "isVersionOf"
        }
    })

    # rights
    id9 = TermIdentification(taxonomy=taxonomy, slug="copyright")
    term9 = current_flask_taxonomies.create_term(id9, extra_data={
        "title": {
            "cs": "Dílo je chráněno podle autorského zákona č. 121/2000 Sb.",
            "en": "This work is protected under the Copyright Act No. 121/2000 Coll."
        }
    })

    # series
    id9 = TermIdentification(taxonomy=taxonomy, slug="maj")
    term9 = current_flask_taxonomies.create_term(id9, extra_data={
        "name": "maj",
        "volume": "1"
    })

    # subject
    id10 = TermIdentification(taxonomy=taxonomy, slug="psh3001")
    term10 = current_flask_taxonomies.create_term(id10, extra_data={
        "title": {
            "cs": "Reynoldsovo číslo",
            "en": "Reynolds number"
        },
        "reletedURI": ["http://psh.techlib.cz/skos/PSH3001"],
        "DateRevised": "2007-01-26T16:14:37"
    })

    id11 = TermIdentification(taxonomy=taxonomy, slug="psh3000")
    term11 = current_flask_taxonomies.create_term(id11, extra_data={
        "title": {
            "cs": "turbulentní proudění",
            "en": "turbulent flow"
        },
        "reletedURI": ["http://psh.techlib.cz/skos/PSH3000"],
        "DateRevised": "2007-01-26T16:14:37"
    })

    id12 = TermIdentification(taxonomy=taxonomy, slug="D010420")
    term12 = current_flask_taxonomies.create_term(id12, extra_data={
        "title": {
            "cs": "pentany",
            "en": "Pentanes"
        },
        "reletedURI": ["http://www.medvik.cz/link/D010420", "http://id.nlm.nih.gov/mesh/D010420"],
        "DateRevised": "2007-01-26T16:14:37",
        "DateCreated": "2007-01-26T16:14:37",
        "DateDateEstablished": "2007-01-26T16:14:37",
    })

    # studyField
    id13 = TermIdentification(taxonomy=taxonomy, slug="O_herectvi-alternativniho-divadla")
    term13 = current_flask_taxonomies.create_term(id13, extra_data={
        "title": {
            "cs": "Herectví alternativního divadla",
        },
        "AKVO": "8203R082"
    })

    # resourceType
    resource_type = current_flask_taxonomies.create_taxonomy("resourceType", extra_data={
        "title":
            {
                "cs": "test_taxonomy",
                "en": "test_taxonomy"
            }
    })

    id14 = TermIdentification(taxonomy=resource_type, slug="datasets")
    term14 = current_flask_taxonomies.create_term(id14, extra_data={
        "title": {
            "cs": "Datasety",
        }
    })

    # languages
    languages = current_flask_taxonomies.create_taxonomy("languages", extra_data={
        "title":
            {
                "cs": "languages",
                "en": "languages"
            }
    })

    id15 = TermIdentification(taxonomy=languages, slug="eng")
    term15 = current_flask_taxonomies.create_term(id15, extra_data={
        "title": {
            "cs": "Anglicky",
        }
    })

    # licenses
    licenses = current_flask_taxonomies.create_taxonomy("licenses", extra_data={
        "title":
            {
                "cs": "licence",
            }
    })

    id16 = TermIdentification(taxonomy=licenses, slug="cc")
    term16 = current_flask_taxonomies.create_term(id16, extra_data={
        "title": {
            "cs": "Licence Creative Commons",
        }
    })

    db.session.commit()


def get_pid():
    """Generates a new PID for a record."""
    record_uuid = uuid.uuid4()
    provider = RecordIdProvider.create(
        object_type='rec',
        object_uuid=record_uuid,
    )
    return record_uuid, provider.pid.pid_value


@pytest.fixture()
def base_json():
    return {
        "$schema": "https://narodni-repozitar.cz/schemas/nr_datasets_metadata/nr-datasets-metadata-v1.0.0.json",
        "abstract": {
            "en": "test abstract",
            "cs": "testovaci abstrakt"
        },
        "access": {
            "files": "restricted",
            "owned_by": [],
            "record": "restricted"
        },
        "creator": "dataset-ingest@cesnet.cz",
        "creators": [
            {
                "affiliations": [
                    {
                        "name": "Trent University"
                    }
                ],
                "person_or_org": {
                    "family_name": "Doe",
                    "given_name": "John",
                    "name": "Doe, John",
                    "type": "personal"
                }
            },
            {
                "affiliations": [
                    {
                        "name": "CESNET"
                    }
                ],
                "person_or_org": {
                    "family_name": "Test",
                    "given_name": "User",
                    "identifiers": [
                        {
                            "identifier": "https://orcid.org/0000-0002-1825-0097",
                            "scheme": "orcid"
                        }
                    ],
                    "name": "Test, User",
                    "type": "personal"
                }
            }
        ],
        "dates": [
            {
                "date": "2020-10-07",
                "type": "created"
            }
        ],
        "identifiers": [
            {
                "identifier": "01.0000/cesnet.000000001",
                "scheme": "handle"
            }
        ],
        "keywords": [
            "test",
            "metadata",
            "dataset"
        ],
        "languages": [
            {
                "links": {
                    "self": "https://narodni-repozitar.cz/2.0/taxonomies/languages/eng"
                }
            }
        ],
        "publication_date": "2020-09-23",
        "related_identifiers": [],
        "resource_type": {
            "type": [
                {
                    "links": {
                        "self": "https://narodni-repozitar.cz/2.0/taxonomies/resourceType/datasets"
                    }
                }
            ]
        },
        "rights": [
            {
                "links": {
                    "self": "https://narodni-repozitar.cz/2.0/taxonomies/licenses/cc"
                }
            }
        ],
        "title": {
            "en": "test dataset title",
            "cs": "nazev testovaciho datasetu"
        }
    }


@pytest.fixture()
def base_json_dereferenced():
    return {
        "$schema": "https://narodni-repozitar.cz/schemas/nr_datasets_metadata/nr-datasets-metadata-v1.0.0.json",
        "abstract": {
            "en": "test abstract",
            "cs": "testovaci abstrakt"
        },
        "access": {
            "files": "restricted",
            "owned_by": [],
            "record": "restricted"
        },
        "creator": "dataset-ingest@cesnet.cz",
        "creators": [
            {
                "affiliations": [
                    {
                        "name": "Trent University"
                    }
                ],
                "person_or_org": {
                    "family_name": "Doe",
                    "given_name": "John",
                    "name": "Doe, John",
                    "type": "personal"
                }
            },
            {
                "affiliations": [
                    {
                        "name": "CESNET"
                    }
                ],
                "person_or_org": {
                    "family_name": "Test",
                    "given_name": "User",
                    "identifiers": [
                        {
                            "identifier": "0000-0002-1825-0097",
                            "scheme": "orcid"
                        }
                    ],
                    "name": "Test, User",
                    "type": "personal"
                }
            }
        ],
        "dates": [
            {
                "date": "2020-10-07",
                "type": "created"
            }
        ],
        "identifiers": [
            {
                "identifier": "01.0000/cesnet.000000001",
                "scheme": "handle"
            }
        ],
        "keywords": [
            "test",
            "metadata",
            "dataset"
        ],
        "languages": [
            {
                "is_ancestor": False,
                "level": 1,
                "links": {
                    "self": "http://127.0.0.1:5000/2.0/taxonomies/languages/eng"
                },
                "title": {
                    "cs": "Anglicky",
                }
            }
        ],
        "publication_date": "2020-09-23",
        "related_identifiers": [],
        "resource_type": {
            "type": [
                {
                    "is_ancestor": False,
                    "level": 1,
                    "links": {
                        "self": "http://127.0.0.1:5000/2.0/taxonomies/resourceType/datasets"
                    },
                    "title": {
                        "cs": "Datasety",
                    }
                }
            ]
        },
        "rights": [
            {
                "is_ancestor": False,
                "level": 1,
                "links": {
                    "self": "http://127.0.0.1:5000/2.0/taxonomies/licenses/cc"
                },
                "title": {
                    "cs": "Licence Creative Commons",
                }
            }
        ],
        "title": {
            "en": "test dataset title",
            "cs": "nazev testovaciho datasetu"
        }
    }
