data "aws_route53_zone" "hosted_zone" {
  name = "${var.hosted_zone_name}."
}

resource "aws_route53_record" "backend" {
  zone_id = "${data.aws_route53_zone.hosted_zone.zone_id}"
  name = "${var.backend_domain}"
  type = "A"

  alias {
    name = "${var.backend_target}"
    zone_id = "${var.backend_zone_id}"
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "frontend" {
  zone_id = "${data.aws_route53_zone.hosted_zone.zone_id}"
  name = "${var.frontend_domain}"
  type = "A"

  alias {
    name = "${var.frontend_target}"
    zone_id = "${var.frontend_zone_id}"
    evaluate_target_health = false
  }
}
