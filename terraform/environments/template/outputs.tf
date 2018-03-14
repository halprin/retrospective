output "beanstalk_env_cname" {
  value = "${aws_elastic_beanstalk_environment.env.cname}"
}

output "frontend_url" {
  value = "${module.frontend.url}"
}

