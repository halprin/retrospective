provider "aws" {
  region = "${var.aws_region}"
}

terraform {
  backend "s3" {
    bucket         = "terraforms-state"
    key            = "retrospective-us-east-1/dev.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform_lock"
  }
}

module "environment" {
  source = "../template"
  application = "${var.beanstalk_application}"
  environment = "dev"
  service_role = "${var.beanstalk_service_role}"
  ec2_key_name = "retrospective"
  notification_email = "${var.notification_email}"
  secret_key = "${var.secret_key}"
}
