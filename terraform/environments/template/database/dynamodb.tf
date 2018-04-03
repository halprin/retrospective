resource "aws_dynamodb_table" "retrospective_table" {
  name           = "retrospective-${var.environment}"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags {
    environment = "${var.environment}"
  }

  lifecycle {
    prevent_destroy = true
  }
}
