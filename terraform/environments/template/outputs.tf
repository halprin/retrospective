output "backend_domain" {
  value = "${data.null_data_source.hostname.outputs.backend}"
}

output "backend_ws_domain" {
  value = "${data.null_data_source.hostname.outputs.backend_websocket}"
}

output "frontend_domain" {
  value = "${data.null_data_source.hostname.outputs.frontend}"
}
