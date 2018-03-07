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

    cd ../environments/${ENVIRONMENT}/
    terraform init
    terraform apply -auto-approve -var "beanstalk_application=${BEANSTALK_APPLICATION}" -var "notification_email=${DEPLOY_EMAIL}" -var "secret_key=${SECRET_KEY}" -var "beanstalk_service_role=${BEANSTALK_SERVICE_ROLE}"
    cd ../../../
}

function deploy_frontend() {
    echo "Deploying frontend"

    cd ./frontend/
    ng build --prod --build-optimizer
    aws s3 sync ./dist/ s3://${APPLICATION}-${ENVIRONMENT}-frontend/ --delete
    cd ../
}

function version_exists() {
    aws elasticbeanstalk describe-application-versions --application-name ${APPLICATION} --version-labels ${1} | jq -e ".ApplicationVersions[] | select(.VersionLabel == \"${1}\")"
    return $?
}

function create_new_version() {
    VERSION=${1}
    echo "Creating version"
    SOURCE_BUNDLE=retrospective_${VERSION}.zip
    git archive -o ${SOURCE_BUNDLE} HEAD
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
version_exists ${GIT_HASH}
if [[ $?  -ne 0 ]]; then
    create_new_version ${GIT_HASH}
else
    echo "Version ${GIT_HASH} already exists"
fi

# deploy new version
DEPLOY_SUCCESS=0
version_already_deployed ${GIT_HASH}
if [[ $?  -ne 0 ]]; then
    deploy_application ${GIT_HASH}
    DEPLOY_SUCCESS=$?
else
    echo "Version ${GIT_HASH} already deployed"
fi

# deploy frontend
deploy_frontend

exit ${DEPLOY_SUCCESS}
