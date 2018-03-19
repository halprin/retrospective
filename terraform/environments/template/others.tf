module "database" {
  source = "database"

  environment = "${var.environment}"
}

module "permissions" {
  source = "permissions"

  environment = "${var.environment}"
  dynamodb_arn = "${module.database.arn}"
}

module "frontend" {
  source = "frontend"

  bucket_name = "${data.null_data_source.hostname.outputs.frontend}"
  environment = "${var.environment}"
}

module "dns" {
  source = "dns"

  environment = "${var.environment}"
  hosted_zone_name = "${var.base_host_name}"

  backend_target = "${aws_elastic_beanstalk_environment.env.cname}"
  backend_zone_id = "${data.aws_elastic_beanstalk_hosted_zone.current.id}"
  backend_domain = "${data.null_data_source.hostname.outputs.backend}"

  frontend_target = "${module.frontend.s3_domain}"
  frontend_zone_id = "${module.frontend.zone_id}"
  frontend_domain = "${data.null_data_source.hostname.outputs.frontend}"
}

data "aws_elastic_beanstalk_hosted_zone" "current" {}

data "null_data_source" "prefix" {
  inputs {
    prefix = "${var.environment != "prod" ? "${var.environment}." : ""}"
  }
}

data "null_data_source" "hostname" {
  inputs {
    backend = "${data.null_data_source.prefix.outputs.prefix}api.retrospective.${var.base_host_name}"
    frontend = "${data.null_data_source.prefix.outputs.prefix}retrospective.${var.base_host_name}"
  }
}
