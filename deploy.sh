#!/usr/bin/env bash

ENVIRONMENT=$1
APPLICATION=retrospective

function run_terraform() {
    echo "Running Terraform"

    pushd ./terraform/environments/${ENVIRONMENT}/
    terraform init
    terraform apply -auto-approve -var "base_host_name=${BASE_HOSTNAME}"
    export BACKEND_ENDPOINT=$(terraform output backend_endpoint)
    export FRONTEND_ENDPOINT=$(terraform output frontend_endpoint)
    popd
}

function deploy_frontend() {
    echo "Deploying frontend"

    pushd ./frontend/
    ./build.sh "${FRONTEND_ENDPOINT}" "${BACKEND_ENDPOINT}"
    aws s3 sync ./dist/ s3://${FRONTEND_ENDPOINT}/ --delete
    popd
}

npm install --silent

# update AWS resources
run_terraform

# deploy frontend
deploy_frontend
