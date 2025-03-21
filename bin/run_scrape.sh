#!/bin/bash
set -e

pushd wordpress
scrapy crawl spider
popd
python ./bin/rehydrate.py ./wordpress/har-output --output ./output

