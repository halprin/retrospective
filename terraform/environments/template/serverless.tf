resource "null_resource" "serverless" {
  provisioner "local-exec" {
    command = "$(npm bin)/serverless deploy"

    working_dir = "../../../"

    environment {
      DATABASE_POLICY = "${module.permissions.database_policy}"
      WEBSOCKET_POLICY = "${module.permissions.websocket_policy}"
      ENVIRONMENT = "${var.environment}"
      ALLOWED_HOST = "${data.null_data_source.hostname.outputs.frontend}"
      WEBSOCKET_ENDPOINT = "https://${data.null_data_source.hostname.outputs.backend_websocket}/retro"
    }
  }

  triggers {
    always = "${uuid()}"
  }
}

data "aws_region" "current" {}

data "external" "api_gateway_id" {
  program = ["aws", "cloudformation", "--region", "${data.aws_region.current.name}", "describe-stacks", "--stack-name", "retrospective-${var.environment}", "--query", "Stacks[0].Outputs[?OutputKey==`ApiGatewayId`].{ApiGatewayId:OutputValue}[0]"]
  depends_on = ["null_resource.serverless"]
}

data "aws_acm_certificate" "certificate" {
  domain      = "${var.base_host_name}"
  most_recent = true
}

resource "aws_api_gateway_domain_name" "custom_domain" {
  domain_name     = "${data.null_data_source.hostname.outputs.backend}"
  certificate_arn = "${data.aws_acm_certificate.certificate.arn}"

  depends_on = ["null_resource.serverless"]
}

resource "aws_api_gateway_base_path_mapping" "custom_domain_pathing" {
  api_id      = "${data.external.api_gateway_id.result["ApiGatewayId"]}"
  stage_name  = "${var.environment}"
  domain_name = "${aws_api_gateway_domain_name.custom_domain.domain_name}"
}
