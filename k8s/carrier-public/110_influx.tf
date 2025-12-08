locals {
  influx_name = "${var.name_prefix}-influx"
}


resource "kubernetes_persistent_volume_claim" "influx" {
  metadata {
    name = local.influx_name
  }
  #
  spec {
    access_modes       = ["ReadWriteOnce"]
    storage_class_name = var.influx_storage_class
    resources {
      requests = {
        storage = var.influx_storage
      }
    }
  }
  #
  wait_until_bound = false
}


resource "kubernetes_deployment" "influx" {
  metadata {
    name = local.influx_name
    labels = {
      name = local.influx_name
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
        name = local.influx_name
      }
    }
    #
    template {
      metadata {
        labels = {
          name = local.influx_name
        }
      }
      #
      spec {
        container {
          name  = local.influx_name
          image = "influxdb:1.8"
          #
          env {
            name  = "INFLUXDB_META_DIR"
            value = "/var/lib/influxdb/meta"
          }
          env {
            name  = "INFLUXDB_DATA_DIR"
            value = "/var/lib/influxdb/data"
          }
          env {
            name  = "INFLUXDB_DATA_WAL_DIR"
            value = "/var/lib/influxdb/wal"
          }
          env {
            name  = "INFLUXDB_HTTP_ENABLED"
            value = "true"
          }
          env {
            name  = "INFLUXDB_DATA_MAX_SERIES_PER_DATABASE"
            value = "0"
          }
          #
          port {
            container_port = 8086
          }
          #
          volume_mount {
            name       = local.influx_name
            mount_path = "/var/lib/influxdb"
          }
        }
        #
        volume {
          name = local.influx_name
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.influx.metadata.0.name
          }
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


resource "kubernetes_service" "influx" {
  metadata {
    name = local.influx_name
  }
  #
  spec {
    selector = {
      name = kubernetes_deployment.influx.metadata.0.name
    }
    #
    port {
      protocol    = "TCP"
      port        = kubernetes_deployment.influx.spec.0.template.0.spec.0.container.0.port.0.container_port
      target_port = kubernetes_deployment.influx.spec.0.template.0.spec.0.container.0.port.0.container_port
    }
  }
}

resource "kubernetes_service" "influx_port" {
  metadata {
    name = "${local.influx_name}-port"
    annotations = {
      "networking.gke.io/load-balancer-ip-addresses" = var.ip_name
    }
  }
  #
  spec {
    selector = {
      name = kubernetes_deployment.influx.metadata.0.name
    }
    #
    port {
      protocol    = "TCP"
      port        = kubernetes_deployment.influx.spec.0.template.0.spec.0.container.0.port.0.container_port
      target_port = kubernetes_deployment.influx.spec.0.template.0.spec.0.container.0.port.0.container_port
    }
    #
    type = "LoadBalancer"
  }
}
