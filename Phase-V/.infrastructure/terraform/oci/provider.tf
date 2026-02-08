# Provider configuration for Terraform
# Part of the OKE Todo Chatbot System deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 5.0.0"
    }
  }
  
  # Configure backend to store state in OCI Object Storage
  backend "s3" {
    bucket   = "todo-chatbot-tf-state"  # This should match the bucket created in storage.tf
    key      = "oke-todo-chatbot/terraform.tfstate"
    region   = "us-ashburn-1"  # This should be configurable
    endpoint = "https://objectstorage.us-ashburn-1.oraclecloud.com"
    
    skip_region_validation      = true
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    force_path_style          = true
  }
}

provider "oci" {
  tenancy_ocid     = var.tenancy_id
  region           = var.region
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
}