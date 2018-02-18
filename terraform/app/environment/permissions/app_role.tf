resource "aws_iam_role" "application_role" {
  name = "retrospective-${var.environment}"
  description = "Allows the Retrospective application in the ${var.environment} environment to interact with other AWS services"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_instance_profile" "instance_profile" {
  name = "${aws_iam_role.application_role.name}"
  role = "${aws_iam_role.application_role.name}"
}

resource "aws_iam_role_policy_attachment" "application_role_to_dynamodb_policy" {
  role       = "${aws_iam_role.application_role.name}"
  policy_arn = "${aws_iam_policy.read_writes_dynamodb.arn}"
}
