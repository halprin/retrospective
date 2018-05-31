resource "aws_dynamodb_table" "retrospective_table" {
  name           = "retrospective-${var.environment}"
  read_capacity  = "${var.read_capacity}"
  write_capacity = "${var.write_capacity}"
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
