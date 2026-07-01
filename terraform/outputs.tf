output "vm_public_ip" {
  description = "Public IP of the Azure VM — add to GitHub secrets as AZURE_VM_IP"
  value       = azurerm_public_ip.main.ip_address
}

output "acr_login_server" {
  description = "ACR login server URL — add to GitHub secrets as ACR_LOGIN_SERVER"
  value       = azurerm_container_registry.main.login_server
}

output "acr_admin_username" {
  description = "ACR admin username — add to GitHub secrets as ACR_USERNAME"
  value       = azurerm_container_registry.main.admin_username
}

output "acr_admin_password" {
  description = "ACR admin password — add to GitHub secrets as ACR_PASSWORD"
  sensitive   = true
  value       = azurerm_container_registry.main.admin_password
}

output "ssh_command" {
  description = "SSH command to connect to your VM"
  value       = "ssh ${var.vm_admin_username}@${azurerm_public_ip.main.ip_address}"
}