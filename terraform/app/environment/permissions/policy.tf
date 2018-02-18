resource "aws_iam_policy" "read_writes_dynamodb" {
  name = "ReadWriteDynamoDbRetrospective-${var.environment}"
  description = "Read and Write to the Retrospective ${var.environment} DynamoDB table"

  policy = "${data.aws_iam_policy_document.read_write_dynamodb.json}"
}

data "aws_iam_policy_document" "read_write_dynamodb" {

  statement {
    sid = "AllowReadingAndWriting"
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
