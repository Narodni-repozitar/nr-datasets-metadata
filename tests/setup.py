
"""Setup for test_module."""
from setuptools import setup

setup(
    name="tests",
    version='1.0.0',
    zip_safe=False,
    packages=['test_module'],
    entry_points={
        "invenio_records.validate":[
            "test = test_module.jsonschemas"
        ],
        'jsonschemas.schemas': [
            'nr_datasets_metadata = nr_datasets_metadata.jsonschemas'
        ],
    },
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
)