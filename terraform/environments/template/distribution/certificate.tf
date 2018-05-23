data "aws_acm_certificate" "certificate" {
  domain = "${var.certificate_name}"
  most_recent = true
}
