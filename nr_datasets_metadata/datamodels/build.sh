#!/bin/sh

#
# Build data model files (like jsonschemas, elasticsearch mappings, ui config,...) from the source specification file.
#
# Run this script from the root of your project.
# e.g. ./nr_datasets_metadata/datamodels/build.sh
#

cd nr_datasets_metadata

models build datamodels/nr-datasets-metadata-v1.0.0.json5
