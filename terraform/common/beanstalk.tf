resource "aws_elastic_beanstalk_application" "retrospective" {
  name = "retrospective"

  lifecycle {
    prevent_destroy = true
  }
}
