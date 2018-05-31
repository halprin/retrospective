module "database" {
  source = "database"

  environment = "${var.environment}"
}

module "permissions" {
  source = "permissions"

  environment  = "${var.environment}"
  dynamodb_arn = "${module.database.arn}"
  hosted_zone_name = "${var.base_host_name}"
}

module "frontend" {
  source = "frontend"

  bucket_name = "${data.null_data_source.hostname.outputs.frontend}"
  environment = "${var.environment}"
}

module "distribution" {
  source = "distribution"

  certificate_name = "${var.base_host_name}"

  frontend_origin_domain = "${module.frontend.s3_domain}"
  frontend_domain = "${data.null_data_source.hostname.outputs.frontend}"

  environment = "${var.environment}"
}

module "dns" {
  source = "dns"

  environment      = "${var.environment}"
  hosted_zone_name = "${var.base_host_name}"

  backend_target  = "${aws_elastic_beanstalk_environment.env.cname}"
  backend_zone_id = "${data.aws_elastic_beanstalk_hosted_zone.current.id}"
  backend_domain  = "${data.null_data_source.hostname.outputs.backend}"

  frontend_target  = "${module.distribution.frontend_domain}"
  frontend_zone_id = "${module.distribution.frontend_zone_id}"
  frontend_domain  = "${data.null_data_source.hostname.outputs.frontend}"
}

resource "aws_security_group" "https" {
  name        = "https-${var.environment}"
  description = "Allow HTTPS communication"

  tags {
    Name = "https-${var.environment}"
    environment = "${var.environment}"
  }
}

resource "aws_security_group_rule" "allow_https_in" {
  type            = "ingress"
  from_port       = 443
  to_port         = 443
  protocol        = "tcp"
  cidr_blocks     = ["0.0.0.0/0"]

  security_group_id = "${aws_security_group.https.id}"
}

resource "aws_security_group_rule" "allow_all_to_anywhere" {
  type            = "egress"
  from_port       = 0
  to_port         = 0
  protocol        = "-1"
  cidr_blocks     = ["0.0.0.0/0"]

  security_group_id = "${aws_security_group.https.id}"
}

data "aws_elastic_beanstalk_hosted_zone" "current" {}

data "null_data_source" "prefix" {
  inputs {
    prefix = "${var.environment != "prod" ? "-${var.environment}" : ""}"
  }
}

data "null_data_source" "hostname" {
  inputs {
    backend  = "retrospective-api${data.null_data_source.prefix.outputs.prefix}.${var.base_host_name}"
    frontend = "retrospective${data.null_data_source.prefix.outputs.prefix}.${var.base_host_name}"
  }
}
