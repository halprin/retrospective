output "beanstalk_application" {
  value = "${aws_elastic_beanstalk_application.retrospective.name}"
}

output "beanstalk_service_role" {
  value = "${data.aws_iam_role.beanstalk_service_role.name}"
}
