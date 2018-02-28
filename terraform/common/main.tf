provider "aws" {
  region = "${var.aws_region}"
}

terraform {
  backend "s3" {
    bucket         = "terraforms-state"
    key            = "retrospective-us-east-1/common.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform_lock"
  }
}
