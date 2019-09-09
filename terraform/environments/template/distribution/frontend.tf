resource "aws_cloudfront_distribution" "frontend" {
  enabled = true

  aliases = ["${var.frontend_domain}"]

  http_version        = "http2"
  default_root_object = "index.html"
  is_ipv6_enabled     = true
  price_class         = "PriceClass_100"

  origin {
    domain_name = "${var.frontend_origin_domain}"
    origin_id   = "${var.environment}-frontend-retrospective"
  }

  default_cache_behavior {
    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    target_origin_id       = "${var.environment}-frontend-retrospective"
    viewer_protocol_policy = "redirect-to-https"

    default_ttl = "${var.environment == "dev" ? 120 : 86400}"
    max_ttl     = "${var.environment == "dev" ? 3600 : 604800}"
    compress    = false

    forwarded_values {
      cookies {
        forward = "none"
      }

      query_string = false
    }
  }

  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 300
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 300
  }

  viewer_certificate {
    acm_certificate_arn      = "${data.aws_acm_certificate.certificate.arn}"
    minimum_protocol_version = "TLSv1.1_2016"
    ssl_support_method       = "sni-only"
  }

  restrictions {
    "geo_restriction" {
      restriction_type = "none"
    }
  }

  tags {
    environment = "${var.environment}"
  }
}
