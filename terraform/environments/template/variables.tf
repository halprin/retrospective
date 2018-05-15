variable "application" {
  type = "string"
}

variable "environment" {
  type = "string"
}

variable "service_role" {
  type = "string"
}

variable "ec2_key_name" {
  type = "string"
}

variable "notification_email" {
  type = "string"
}

variable "secret_key" {
  type = "string"
}

variable "base_host_name" {
  type = "string"
}

variable "message_broker_address" {
  type = "string"
}

variable "message_broker_security_group" {
  type = "string"
}
