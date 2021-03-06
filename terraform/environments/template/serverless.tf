resource "null_resource" "serverless" {
  provisioner "local-exec" {
    command = "$(npm bin)/serverless deploy"

    working_dir = "../../../"

    environment {
      DATABASE_POLICY    = "${module.permissions.database_policy}"
      WEBSOCKET_POLICY   = "${module.permissions.websocket_policy}"
      ENVIRONMENT        = "${var.environment}"
      ALLOWED_HOST       = "${data.null_data_source.hostname.outputs.frontend}"
      WEBSOCKET_ENDPOINT = "https://${data.null_data_source.hostname.outputs.backend_websocket}/retro"
    }
  }

  triggers {
    always = "${uuid()}"
  }
}

data "aws_region" "current" {}

data "external" "api_gateway_id" {
  program    = ["aws", "cloudformation", "--region", "${data.aws_region.current.name}", "describe-stacks", "--stack-name", "retrospective-${var.environment}", "--query", "Stacks[0].Outputs[?OutputKey==`ApiGatewayId`].{ApiGatewayId:OutputValue}[0]"]
  depends_on = ["null_resource.serverless"]
}

data "external" "ws_api_gateway_id" {
  program    = ["aws", "apigatewayv2", "--region", "${data.aws_region.current.name}", "--no-paginate", "get-apis", "--query", "Items[?Name==`${var.environment}-retrospective-websockets`].{WsApiGatewayId:ApiId}[0]"]
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

//https://github.com/terraform-providers/terraform-provider-aws/issues/7004
resource "null_resource" "custom_ws_domain" {
  provisioner "local-exec" {
    command = "aws apigatewayv2 create-domain-name --domain-name ${data.null_data_source.hostname.outputs.backend_websocket} --domain-name-configurations 'CertificateArn=${data.aws_acm_certificate.certificate.arn},EndpointType=REGIONAL'"
  }

  depends_on = ["null_resource.serverless"]

  triggers {
    if_not_exists = "${data.null_data_source.hostname.outputs.backend_websocket}"
  }
}

data "external" "custom_ws_domain" {
  program    = ["aws", "apigatewayv2", "--region", "${data.aws_region.current.name}", "get-domain-name", "--domain-name", "${data.null_data_source.hostname.outputs.backend_websocket}", "--query", "{DomainName:DomainName,AwsDomainName:DomainNameConfigurations[0].ApiGatewayDomainName,AwsHozedZone:DomainNameConfigurations[0].HostedZoneId}"]
  depends_on = ["null_resource.custom_ws_domain"]
}

resource "aws_api_gateway_base_path_mapping" "custom_ws_domain_pathing" {
  api_id      = "${data.external.ws_api_gateway_id.result["WsApiGatewayId"]}"
  stage_name  = "${var.environment}"
  domain_name = "${data.external.custom_ws_domain.result["DomainName"]}"
  base_path   = "retro"
}
