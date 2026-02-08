# Terraform configuration for OKE cluster
# Part of the OKE Todo Chatbot System deployment

resource "oci_containerengine_cluster" "todo_chatbot_cluster" {
  compartment_id = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name = var.cluster_name
  vcn_id = oci_core_virtual_network.todo_chatbot_vcn.id
  endpoint_config {
    is_public_ip_enabled = true
  }
  options {
    service_lb_subnet_ids = [
      oci_core_subnet.public_subnet_ad1.id,
      oci_core_subnet.public_subnet_ad2.id
    ]
    add_ons {
      is_kubernetes_dashboard_enabled = false
      is_tiller_enabled = false
    }
    kubernetes_network_config {
      pods_cidr     = "10.244.0.0/16"
      services_cidr = "10.96.0.0/16"
    }
  }
}

resource "oci_containerengine_node_pool" "todo_chatbot_node_pool" {
  cluster_id         = oci_containerengine_cluster.todo_chatbot_cluster.id
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = "${var.cluster_name}-nodepool"
  node_image_name    = var.node_image_name
  node_shape         = var.node_shape
  quantity_per_subnet = 1
  subnet_ids         = [
    oci_core_subnet.private_subnet_ad1.id,
    oci_core_subnet.private_subnet_ad2.id
  ]

  node_config_details {
    placement_configs {
      availability_domain = data.oci_identity_availability_domains.ADs.availability_domains[0].name
      subnet_id           = oci_core_subnet.private_subnet_ad1.id
    }
    placement_configs {
      availability_domain = data.oci_identity_availability_domains.ADs.availability_domains[1].name
      subnet_id           = oci_core_subnet.private_subnet_ad2.id
    }
    size = 1
  }

  ssh_public_key = var.ssh_public_key
}