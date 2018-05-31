resource "aws_iam_policy" "read_writes_dynamodb" {
  name        = "ReadWriteDynamoDbRetrospective-${var.environment}"
  description = "Read and Write to the Retrospective ${var.environment} DynamoDB table"

  policy = "${data.aws_iam_policy_document.read_write_dynamodb.json}"
}

data "aws_iam_policy_document" "read_write_dynamodb" {
  statement {
    sid    = "AllowReadingAndWriting"
    effect = "Allow"

    actions = [
      "dynamodb:BatchGetItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan",
      "dynamodb:CreateBackup",
      "dynamodb:DescribeStream",
      "dynamodb:Query",
      "dynamodb:UpdateItem",
      "dynamodb:DescribeTable",
      "dynamodb:GetShardIterator",
      "dynamodb:RestoreTableFromBackup",
      "dynamodb:GetItem",
      "dynamodb:DescribeContinuousBackups",
      "dynamodb:DeleteBackup",
      "dynamodb:DescribeBackup",
      "dynamodb:UpdateTable",
      "dynamodb:GetRecords",
    ]

    resources = ["${var.dynamodb_arn}"]
  }
}

resource "aws_iam_policy" "letsencrypt_authorize" {
  name        = "LetsEncryptAuthorization-${var.environment}"
  description = "Allows Let's Encrypt to authorize the web server in the ${var.environment}"

  policy = "${data.aws_iam_policy_document.letsencrypt_authorize.json}"
}

data "aws_route53_zone" "hosted_zone" {
  name = "${var.hosted_zone_name}."
}

data "aws_iam_policy_document" "letsencrypt_authorize" {
  statement {
    sid    = "AllowModifyHostedZone"
    effect = "Allow"

    actions = [
      "route53:GetChange",
      "route53:ChangeResourceRecordSets",
    ]

    resources = [
      "arn:aws:route53:::change/*",
      "arn:aws:route53:::hostedzone/${data.aws_route53_zone.hosted_zone.zone_id}"
    ]
  }

  statement {
    sid    = "AllowListZones"
    effect = "Allow"

    actions = [
      "route53:ListHostedZones",
    ]

    resources = ["*"]
  }
}
