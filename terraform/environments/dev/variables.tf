variable "aws_region" {
  type = "string"
  default = "us-east-1"
}

variable "beanstalk_application" {
  type = "string"
}

variable "secret_key" {
  type = "string"
}

variable "notification_email" {
  type = "string"
}

variable "beanstalk_service_role" {
  type = "string"
}

variable "base_host_name" {
  type = "string"
}
