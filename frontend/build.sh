#!/usr/bin/env bash

FRONTEND_ENDPOINT="${1}"
BACKEND_ENDPOINT="${2}"

npm install --silent

sed -i '' -e "s|BACKEND_ENDPOINT|${BACKEND_ENDPOINT}|" ./src/environments/environment.prod.ts
sed -i '' -e "s|FRONTEND_ENDPOINT|${FRONTEND_ENDPOINT}|" ./src/environments/environment.prod.ts;

$(npm bin)/ng build --prod --build-optimizer
