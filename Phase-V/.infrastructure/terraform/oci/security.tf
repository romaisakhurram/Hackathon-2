# Terraform configuration for compartments and security lists
# Part of the OKE Todo Chatbot System deployment

# Security list for public subnets
resource "oci_core_security_list" "public_security_list" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_virtual_network.todo_chatbot_vcn.id
  display_name   = "Public Security List"

  # Allow outbound HTTPS traffic
  egress_security_rules {
    protocol    = "6"  # TCP
    destination = "0.0.0.0/0"
    tcp_options {
      max = 443
      min = 443
    }
  }

  # Allow outbound HTTP traffic
  egress_security_rules {
    protocol    = "6"  # TCP
    destination = "0.0.0.0/0"
    tcp_options {
      max = 80
      min = 80
    }
  }

  # Allow inbound SSH traffic
  ingress_security_rules {
    protocol = "6"  # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 22
      min = 22
    }
  }

  # Allow inbound HTTPS traffic
  ingress_security_rules {
    protocol = "6"  # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 443
      min = 443
    }
  }

  # Allow inbound HTTP traffic
  ingress_security_rules {
    protocol = "6"  # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 80
      min = 80
    }
  }

  # Allow inbound traffic from the same security list
  ingress_security_rules {
    protocol = "all"
    source   = "10.0.0.0/16"
  }
}

# Security list for private subnets
resource "oci_core_security_list" "private_security_list" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_virtual_network.todo_chatbot_vcn.id
  display_name   = "Private Security List"

  # Allow outbound traffic to the internet
  egress_security_rules {
    protocol    = "6"  # TCP
    destination = "0.0.0.0/0"
  }

  # Allow inbound traffic from the VCN
  ingress_security_rules {
    protocol = "all"
    source   = "10.0.0.0/16"
  }

  # Allow inbound ICMP traffic from the VCN
  ingress_security_rules {
    protocol = "1"  # ICMP
    source   = "10.0.0.0/16"
  }
}

# Route table for public subnets
resource "oci_core_route_table" "public_route_table" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_virtual_network.todo_chatbot_vcn.id
  display_name   = "Public Route Table"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.internet_gateway.id
  }
}

# Internet gateway
resource "oci_core_internet_gateway" "internet_gateway" {
  compartment_id = var.compartment_id
  display_name   = "Internet Gateway"
  vcn_id         = oci_core_virtual_network.todo_chatbot_vcn.id
}

# Compartment for the application (if needed)
resource "oci_identity_compartment" "todo_chatbot_compartment" {
  count = var.create_compartment ? 1 : 0
  
  compartment_id = var.tenancy_id
  description    = "Compartment for Todo Chatbot System"
  name           = "TodoChatbotCompartment"
}