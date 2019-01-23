output "backend_endpoint" {
  value = "${module.environment.backend_domain}"
}

output "backend_ws_endpoint" {
  value = "${module.environment.backend_ws_domain}"
}

output "frontend_endpoint" {
  value = "${module.environment.frontend_domain}"
}
