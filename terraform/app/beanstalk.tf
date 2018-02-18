resource "aws_elastic_beanstalk_application" "retrospective" {
  name        = "retrospective"
}

module "dev_environment" {
  source = "./environment"
  application = "${aws_elastic_beanstalk_application.retrospective.name}"
  environment = "dev"
  service_role = "${var.service_role}"
  ec2_key_name = "retrospective"
  notification_email = "${var.notification_email}"
  secret_key = "${var.secret_key}"
}

module "prod_environment" {
  source = "./environment"
  application = "${aws_elastic_beanstalk_application.retrospective.name}"
  environment = "prod"
  service_role = "${var.service_role}"
  ec2_key_name = "retrospective"
  notification_email = "${var.notification_email}"
  secret_key = "${var.secret_key}"
}
