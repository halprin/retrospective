provider "aws" {
  region = "${var.aws_region}"
}

terraform {
  backend "s3" {
    bucket         = "terraforms-state"
    key            = "retrospective-us-east-1/prod.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform_lock"
  }
}

module "environment" {
  source                       = "../template"
  environment                  = "prod"
  base_host_name               = "${var.base_host_name}"
  dynamodb_read_write_capacity = "5"
}
