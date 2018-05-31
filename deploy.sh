#!/usr/bin/env bash

ENVIRONMENT=$1
APPLICATION=retrospective

function run_terraform() {
    echo "Running Terraform"

    cd ./terraform/common/
    terraform init
    terraform apply -auto-approve
    BEANSTALK_APPLICATION=$(terraform output beanstalk_application)
    BEANSTALK_SERVICE_ROLE=$(terraform output beanstalk_service_role)
    MESSAGE_BROKER_ADDRESS=$(terraform output message_broker_address)
    MESSAGE_BROKER_SECURITY_GROUP=$(terraform output message_broker_security_group)

    cd ../environments/${ENVIRONMENT}/
    terraform init
    terraform apply -auto-approve -var "beanstalk_application=${BEANSTALK_APPLICATION}" -var "notification_email=${DEPLOY_EMAIL}" -var "secret_key=${SECRET_KEY}" -var "beanstalk_service_role=${BEANSTALK_SERVICE_ROLE}" -var "base_host_name=${BASE_HOSTNAME}" -var "message_broker_address=${MESSAGE_BROKER_ADDRESS}" -var "message_broker_security_group=${MESSAGE_BROKER_SECURITY_GROUP}"
    export BACKEND_ENDPOINT=$(terraform output backend_endpoint)
    export FRONTEND_ENDPOINT=$(terraform output frontend_endpoint)
    cd ../../../
}

function deploy_frontend() {
    echo "Deploying frontend"

    cd ./frontend/
    npm install --silent
    ./build.sh "${FRONTEND_ENDPOINT}" "${BACKEND_ENDPOINT}"
    aws s3 sync ./dist/ s3://${FRONTEND_ENDPOINT}/ --delete
    cd ../
}

function version_exists() {
    VERSION=${1}
    aws elasticbeanstalk describe-application-versions --application-name ${APPLICATION} --version-labels ${VERSION} | jq -e ".ApplicationVersions[] | select(.VersionLabel == \"${VERSION}\")"
    return $?
}

function create_new_version() {
    VERSION=${1}
    echo "Creating version"

    sed -i '' -e "s|BASE_HOSTNAME|${BASE_HOSTNAME}|" ./.ebextensions/container.config
    sed -i '' -e "s|DEPLOY_EMAIL|${DEPLOY_EMAIL}|" ./.ebextensions/container.config

    SOURCE_BUNDLE=retrospective_${VERSION}.zip
    STASH_NAME=`git stash create`
    git archive -o ${SOURCE_BUNDLE} ${STASH_NAME}
    aws s3 cp ./${SOURCE_BUNDLE} s3://${BEANSTALK_S3_BUCKET}/
    aws elasticbeanstalk create-application-version --application-name ${APPLICATION} --version-label ${VERSION} --source-bundle S3Bucket=${BEANSTALK_S3_BUCKET},S3Key=${SOURCE_BUNDLE}
}

function version_already_deployed() {
    VERSION=${1}
    aws elasticbeanstalk describe-environments --application-name ${APPLICATION} --environment-names ${APPLICATION}-${ENVIRONMENT} | jq -e ".Environments[] | select(.VersionLabel == \"${VERSION}\")"
    return $?
}

function wait_for_complete_deployment() {
    aws elasticbeanstalk describe-environments --application-name ${APPLICATION} --environment-names ${APPLICATION}-${ENVIRONMENT} | jq -e '.Environments[] | select(.Status == "Ready")'
    DEPLOYMENT_COMPLETE=$?
    SLEEP_LENGTH=30
    TOTAL_SLEEP_LENGTH=0

    while [[ ${DEPLOYMENT_COMPLETE} -ne 0 ]]; do
        if [[ ${TOTAL_SLEEP_LENGTH} -gt 1500 ]]; then
            echo "Done waiting for deployment to complete."
            return 1
        fi
        echo "Waiting for deployment to complete.  Waited ${TOTAL_SLEEP_LENGTH} seconds thus far."
        sleep ${SLEEP_LENGTH}
        TOTAL_SLEEP_LENGTH=$(($TOTAL_SLEEP_LENGTH + $SLEEP_LENGTH))
        aws elasticbeanstalk describe-environments --application-name ${APPLICATION} --environment-names ${APPLICATION}-${ENVIRONMENT} | jq -e '.Environments[] | select(.Status == "Ready")'
        DEPLOYMENT_COMPLETE=$?
    done

    return 0
}

function deploy_application() {
    VERSION=${1}
    echo "Deploying version ${VERSION}"
    aws elasticbeanstalk update-environment --application-name ${APPLICATION} --environment-name ${APPLICATION}-${ENVIRONMENT} --version-label ${VERSION}
    wait_for_complete_deployment
    return $?
}

# update AWS resources
run_terraform

# create new version
GIT_HASH=$(git rev-parse --short --verify HEAD)
MASTER_VERSION=${GIT_HASH}

version_exists ${MASTER_VERSION}
if [[ $?  -ne 0 ]]; then
    create_new_version ${MASTER_VERSION}
else
    echo "Version ${MASTER_VERSION} already exists"
fi

# deploy new version
DEPLOY_SUCCESS=0
version_already_deployed ${MASTER_VERSION}
if [[ $?  -ne 0 ]]; then
    deploy_application ${MASTER_VERSION}
    DEPLOY_SUCCESS=$?
else
    echo "Version ${MASTER_VERSION} already deployed"
fi

# deploy frontend
deploy_frontend

exit ${DEPLOY_SUCCESS}
