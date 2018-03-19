output "s3_domain" {
  value = "${aws_s3_bucket.frontend.website_domain}"
}

output "zone_id" {
  value = "${aws_s3_bucket.frontend.hosted_zone_id}"
}
