output "database_policy" {
  value = "${aws_iam_policy.read_writes_dynamodb.arn}"
}
