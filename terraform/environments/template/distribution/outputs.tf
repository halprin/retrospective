output "frontend_domain" {
  value = "${aws_cloudfront_distribution.frontend.domain_name}"
}

output "frontend_zone_id" {
  value = "${aws_cloudfront_distribution.frontend.hosted_zone_id}"
}
