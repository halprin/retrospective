output "database_policy" {
  value = "${aws_iam_policy.read_writes_dynamodb.arn}"
}

output "websocket_policy" {
  value = "${aws_iam_policy.manage_websocket_connections.arn}"
}
