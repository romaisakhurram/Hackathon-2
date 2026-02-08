# Terraform configuration for Virtual Cloud Network (VCN) and subnets
# Part of the OKE Todo Chatbot System deployment

resource "oci_core_virtual_network" "todo_chatbot_vcn" {
  cidr_block     = "10.0.0.0/16"
  compartment_id = var.compartment_id
  display_name   = "todo-chatbot-vcn"
  dns_label      = "todochatbotvcn"
}

resource "oci_core_subnet" "public_subnet_ad1" {
  availability_domain = data.oci_identity_availability_domains.ADs.availability_domains[0].name
  cidr_block          = "10.0.10.0/24"
  display_name        = "Public Subnet AD-1"
  dns_label           = "pubsubnet1"
  security_list_ids   = [oci_core_security_list.public_security_list.id]
  vcn_id              = oci_core_virtual_network.todo_chatbot_vcn.id
  route_table_id      = oci_core_route_table.public_route_table.id
  dhcp_options_id     = oci_core_virtual_network.todo_chatbot_vcn.default_dhcp_options_id
}

resource "oci_core_subnet" "public_subnet_ad2" {
  availability_domain = data.oci_identity_availability_domains.ADs.availability_domains[1].name
  cidr_block          = "10.0.11.0/24"
  display_name        = "Public Subnet AD-2"
  dns_label           = "pubsubnet2"
  security_list_ids   = [oci_core_security_list.public_security_list.id]
  vcn_id              = oci_core_virtual_network.todo_chatbot_vcn.id
  route_table_id      = oci_core_route_table.public_route_table.id
  dhcp_options_id     = oci_core_virtual_network.todo_chatbot_vcn.default_dhcp_options_id
}

resource "oci_core_subnet" "private_subnet_ad1" {
  availability_domain = data.oci_identity_availability_domains.ADs.availability_domains[0].name
  cidr_block          = "10.0.20.0/24"
  display_name        = "Private Subnet AD-1"
  dns_label           = "privsubnet1"
  security_list_ids   = [oci_core_security_list.private_security_list.id]
  vcn_id              = oci_core_virtual_network.todo_chatbot_vcn.id
  dhcp_options_id     = oci_core_virtual_network.todo_chatbot_vcn.default_dhcp_options_id
  prohibit_public_ip_on_vnic = true
}

resource "oci_core_subnet" "private_subnet_ad2" {
  availability_domain = data.oci_identity_availability_domains.ADs.availability_domains[1].name
  cidr_block          = "10.0.21.0/24"
  display_name        = "Private Subnet AD-2"
  dns_label           = "privsubnet2"
  security_list_ids   = [oci_core_security_list.private_security_list.id]
  vcn_id              = oci_core_virtual_network.todo_chatbot_vcn.id
  dhcp_options_id     = oci_core_virtual_network.todo_chatbot_vcn.default_dhcp_options_id
  prohibit_public_ip_on_vnic = true
}

# Data source to get availability domains
data "oci_identity_availability_domains" "ADs" {
  compartment_id = var.compartment_id
}