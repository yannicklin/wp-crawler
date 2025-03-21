#!/bin/bash
set -e

if [[ "${FEATURE}" == "NONE" || -z "${FEATURE}" ]]
then
  export DOMAIN="${DOMAIN}"
  export FEATURE=""
else
  export DOMAIN="${FEATURE}-${DOMAIN}"
fi

echo ${FEATURE}
echo ${DOMAIN}
pushd wordpress
scrapy crawl spider
popd

if [[ "${FEATURE}" != "NONE" && -n "${FEATURE}" ]]; then
  subdomain="${FEATURE}"
elif [[ "${DOMAIN}" == 'wordpress.stg.ctm.zone' ]]; then
  subdomain='feature-stg'
else
  subdomain='feature-dev'
fi

python ./bin/rehydrate.py ./wordpress/har-output --output ./output --use-domain ${subdomain}.ctm-cf-page-enterprise-wordpress.pages.dev
