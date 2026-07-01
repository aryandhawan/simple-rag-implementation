variable "Ragbot_resource_group" {
  type        = string
  description = "RAG bot for AI/ML concepts"
  default     = "ragbot-rg"
}

variable "subscription_id" {
  type        = string
  description = "Azure subscription ID"
}

variable "location" {
  type        = string
  description = "Azure region"
  default     = "East Asia"
}

variable "vm_size" {
  type        = string
  description = "Azure VM size"
  default     = "Standard_B1s"
}

variable "acr_name" {
  type        = string
  description = "Azure Container Registry name — must be globally unique"
  default     = "aryanragbot"
}

variable "vm_admin_username" {
  type        = string
  description = "Admin username for the VM"
  default     = "azureuser"
}

variable "ssh_public_key_path" {
  type        = string
  description = "Path to your SSH public key"
  default     = "~/.ssh/id_rsa.pub"
}