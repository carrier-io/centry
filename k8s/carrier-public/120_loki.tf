locals {
  loki_name = "${var.name_prefix}-loki"
}

resource "kubernetes_deployment" "loki" {
  metadata {
    name = local.loki_name
    labels = {
      name = local.loki_name
    }
  }
  #
  spec {
    replicas = 1
    strategy {
      type = "Recreate"
    }
    #
    selector {
      match_labels = {
        name = local.loki_name
      }
    }
    #
    template {
      metadata {
        labels = {
          name = local.loki_name
        }
      }
      #
      spec {
        container {
          name  = local.loki_name
          image = "grafana/loki:2.3.0"
          #
          #
          port {
            container_port = 3100
          }
          #
        }
        #
        restart_policy                   = "Always"
        termination_grace_period_seconds = 30
      }
    }
  }
  #
  wait_for_rollout = false
}


resource "kubernetes_service" "loki" {
  metadata {
    name = local.loki_name
  }
  #
  spec {
    selector = {
      name = kubernetes_deployment.loki.metadata.0.name
    }
    #
    port {
      protocol    = "TCP"
      port        = kubernetes_deployment.loki.spec.0.template.0.spec.0.container.0.port.0.container_port
      target_port = kubernetes_deployment.loki.spec.0.template.0.spec.0.container.0.port.0.container_port
    }
  }
}

resource "kubernetes_service" "loki_port" {
  metadata {
    name = "${local.loki_name}-port"
  }
  #
  spec {
    selector = {
      name = kubernetes_deployment.loki.metadata.0.name
    }
    #
    port {
      protocol    = "TCP"
      port        = kubernetes_deployment.loki.spec.0.template.0.spec.0.container.0.port.0.container_port
      target_port = kubernetes_deployment.loki.spec.0.template.0.spec.0.container.0.port.0.container_port
    }
    #
    type = "LoadBalancer"
    load_balancer_ip = "34.132.179.209"
  }
}
