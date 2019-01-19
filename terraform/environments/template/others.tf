module "database" {
  source = "database"

  read_capacity  = "${var.dynamodb_read_write_capacity}"
  write_capacity = "${var.dynamodb_read_write_capacity}"
  environment    = "${var.environment}"
}

module "permissions" {
  source = "permissions"

  environment      = "${var.environment}"
  dynamodb_arn     = "${module.database.arn}"
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
  frontend_domain        = "${data.null_data_source.hostname.outputs.frontend}"

  environment = "${var.environment}"
}

module "dns" {
  source = "dns"

  environment      = "${var.environment}"
  hosted_zone_name = "${var.base_host_name}"

  backend_target  = "${aws_api_gateway_domain_name.custom_domain.cloudfront_domain_name}"
  backend_zone_id = "${aws_api_gateway_domain_name.custom_domain.cloudfront_zone_id}"
  backend_domain  = "${data.null_data_source.hostname.outputs.backend}"

  frontend_target  = "${module.distribution.frontend_domain}"
  frontend_zone_id = "${module.distribution.frontend_zone_id}"
  frontend_domain  = "${data.null_data_source.hostname.outputs.frontend}"
}

data "null_data_source" "prefix" {
  inputs {
    prefix = "${var.environment != "prod" ? "-${var.environment}" : ""}"
  }
}

data "null_data_source" "hostname" {
  inputs {
    backend  = "retrospective-api${data.null_data_source.prefix.outputs.prefix}.${var.base_host_name}"
    backend_websocket = "retrospective-ws${data.null_data_source.prefix.outputs.prefix}.${var.base_host_name}"
    frontend = "retrospective${data.null_data_source.prefix.outputs.prefix}.${var.base_host_name}"
  }
}
