# Variables for Terraform configuration
# Part of the OKE Todo Chatbot System deployment

variable "tenancy_id" {
  description = "OCID of the tenancy"
  type        = string
}

variable "compartment_id" {
  description = "OCID of the compartment where resources will be created"
  type        = string
}

variable "cluster_name" {
  description = "Name of the OKE cluster"
  type        = string
  default     = "todo-chatbot-cluster"
}

variable "kubernetes_version" {
  description = "Version of Kubernetes to use for the cluster"
  type        = string
}

variable "node_shape" {
  description = "Shape of the nodes in the node pool"
  type        = string
  default     = "VM.Standard.E4.Flex"
}

variable "node_image_name" {
  description = "Image name for the nodes in the node pool"
  type        = string
  default     = "Oracle-Linux-8"
}

variable "ssh_public_key" {
  description = "SSH public key to be used for the nodes"
  type        = string
}

variable "create_compartment" {
  description = "Whether to create a new compartment for the resources"
  type        = bool
  default     = false
}

variable "region" {
  description = "OCI region where resources will be created"
  type        = string
}