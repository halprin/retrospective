data "null_data_source" "local" {
  inputs {
    bucket_name = "retrospective-${var.environment}-frontend"
  }
}

resource "aws_s3_bucket" "frontend" {
  bucket = "${data.null_data_source.local.outputs.bucket_name}"

  acl = "private"
  policy = "${data.aws_iam_policy_document.allow_public.json}"

  website {
    index_document = "index.html"
    error_document = "index.html"
  }

  tags {
    environment = "${var.environment}"
  }
}

data "aws_iam_policy_document" "allow_public" {
  statement {
    sid = "PublicReadGetObject"
    effect = "Allow"
    principals {
      identifiers = ["*"]
      type = "AWS"
    }
    actions = ["s3:GetObject"]
    resources = ["arn:aws:s3:::${data.null_data_source.local.outputs.bucket_name}/*"]
  }
}
