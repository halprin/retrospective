#!/usr/bin/env bash

sed -i '' -e "s|BACKEND_ENDPOINT|${BACKEND_ENDPOINT}|" ./src/environments/environment.ts
sed -i '' -e "s|FRONTEND_ENDPOINT|${FRONTEND_ENDPOINT}|" ./src/environments/environment.ts;

ng serve
