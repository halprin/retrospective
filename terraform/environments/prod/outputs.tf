output "backend_endpoint" {
  value = "${module.environment.beanstalk_env_cname}"
}

output "frontend_endpoint" {
  value = "${module.environment.frontend_url}"
}
