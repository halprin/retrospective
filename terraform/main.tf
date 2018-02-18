provider "aws" {
  region = "${var.aws_region}"
}

terraform {
  backend "s3" {
    bucket         = "terraforms-state"
    key            = "retrospective-us-east-1/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform_lock"
  }
}

module "application" {
  source = "./app"

  secret_key = "${var.secret_key}"
  notification_email = "${var.notification_email}"
  service_role = "${data.aws_iam_role.beanstalk_service_role.name}"
}
