output "beanstalk_application" {
  value = "${aws_elastic_beanstalk_application.retrospective.name}"
}

output "beanstalk_service_role" {
  value = "${data.aws_iam_role.beanstalk_service_role.name}"
}

output "message_broker_address" {
  value = "${aws_elasticache_cluster.message_broker.cache_nodes.0.address}"
}

output "message_broker_security_group" {
  value = "${aws_security_group.redis.id}"
}
