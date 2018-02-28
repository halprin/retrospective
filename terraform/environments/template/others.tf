module "database" {
  source = "database"

  environment = "${var.environment}"
}

module "permissions" {
  source = "permissions"

  environment = "${var.environment}"
  dynamodb_arn = "${module.database.arn}"
}
