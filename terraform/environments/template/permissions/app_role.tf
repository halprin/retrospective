resource "aws_iam_role" "application_role" {
  name        = "retrospective-${var.environment}"
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

resource "aws_iam_role_policy_attachment" "application_role_to_letsencrypt_policy" {
  role       = "${aws_iam_role.application_role.name}"
  policy_arn = "${aws_iam_policy.letsencrypt_authorize.arn}"
}

resource "aws_iam_role_policy_attachment" "application_role_to_t_unlimited_policy" {
  role       = "${aws_iam_role.application_role.name}"
  policy_arn = "${aws_iam_policy.change_t_unlimited.arn}"
}

data "aws_iam_policy" "AWSElasticBeanstalkWebTier" {
  arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
}

data "aws_iam_policy" "AWSElasticBeanstalkMulticontainerDocker" {
  arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker"
}

data "aws_iam_policy" "AWSElasticBeanstalkWorkerTier" {
  arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier"
}

resource "aws_iam_role_policy_attachment" "application_role_to_eb_web_policy" {
  role       = "${aws_iam_role.application_role.name}"
  policy_arn = "${data.aws_iam_policy.AWSElasticBeanstalkWebTier.arn}"
}

resource "aws_iam_role_policy_attachment" "application_role_to_eb_docker_policy" {
  role       = "${aws_iam_role.application_role.name}"
  policy_arn = "${data.aws_iam_policy.AWSElasticBeanstalkMulticontainerDocker.arn}"
}

resource "aws_iam_role_policy_attachment" "application_role_to_eb_worker_policy" {
  role       = "${aws_iam_role.application_role.name}"
  policy_arn = "${data.aws_iam_policy.AWSElasticBeanstalkWorkerTier.arn}"
}
