output "backend_domain" {
  value = "${data.null_data_source.hostname.outputs.backend}"
}

output "frontend_domain" {
  value = "${data.null_data_source.hostname.outputs.frontend}"
}
