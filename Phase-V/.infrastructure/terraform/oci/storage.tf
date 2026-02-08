# Terraform configuration for object storage bucket
# Part of the OKE Todo Chatbot System deployment

resource "oci_objectstorage_bucket" "todo_chatbot_state_bucket" {
  compartment_id = var.compartment_id
  name           = "${var.bucket_name_prefix}-tf-state"
  namespace      = var.object_storage_namespace
  # Keep older versions of objects in the bucket
  versioning     = "Enabled"
  
  # Define the type of storage to use
  storage_tier   = "Standard"
  
  # Configure the bucket to be immediately deleted when removed from config
  # In production, you'd want to set this to "false" to prevent accidental data loss
  force_destroy  = true
}

# Variables for the storage configuration
variable "bucket_name_prefix" {
  description = "Prefix for the bucket name"
  type        = string
  default     = "todo-chatbot"
}

variable "object_storage_namespace" {
  description = "Object storage namespace"
  type        = string
}

variable "compartment_id" {
  description = "Compartment ID where the bucket will be created"
  type        = string
}