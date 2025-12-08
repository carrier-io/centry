resource "kubernetes_ingress_v1" "ingress" {
  metadata {
    name = "${var.name_prefix}-ingress"
    annotations = {
      "kubernetes.io/ingress.global-static-ip-name" = var.ip_name
      "networking.gke.io/managed-certificates"      = var.ssl_cert_name
    }
  }

  spec {
    rule {
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          #
          backend {
            service {
              name = kubernetes_service.pylon_main.metadata.0.name
              port {
                name = kubernetes_service.pylon_main.spec.0.port.0.name
              }
            }
          }
        }
      }
    }
  }
}
