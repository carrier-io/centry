locals {
  redis_name = "${var.name_prefix}-redis"
}


resource "kubernetes_secret" "redis" {
  metadata {
    name = local.redis_name
  }
  #
  data = {
    password = var.redis_password
  }
}


resource "kubernetes_persistent_volume_claim" "redis" {
  metadata {
    name = local.redis_name
  }
  #
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = var.redis_storage
      }
    }
  }
  #
  wait_until_bound = false
}


resource "kubernetes_deployment" "redis" {
  metadata {
    name = local.redis_name
    labels = {
      name = local.redis_name
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
        name = local.redis_name
      }
    }
    #
    template {
      metadata {
        labels = {
          name = local.redis_name
        }
      }
      #
      spec {
        container {
          name  = local.redis_name
          image = "redis:alpine"
          #
          command = [
            "sh"
          ]
          args = [
            "-c",
            "exec redis-server --requirepass $$REDIS_PASSWORD --save 300 1 --dir /data/ --dbfilename dump.rdb"
          ]
          #
          env {
            name = "REDIS_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.redis.metadata.0.name
                key  = "password"
              }
            }
          }
          #
          port {
            container_port = 6379
          }
          #
          volume_mount {
            name       = local.redis_name
            mount_path = "/data"
          }
        }
        #
        volume {
          name = local.redis_name
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.redis.metadata.0.name
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


resource "kubernetes_service" "redis" {
  metadata {
    name = local.redis_name
  }
  #
  spec {
    selector = {
      name = kubernetes_deployment.redis.metadata.0.name
    }
    #
    port {
      protocol    = "TCP"
      port        = kubernetes_deployment.redis.spec.0.template.0.spec.0.container.0.port.0.container_port
      target_port = kubernetes_deployment.redis.spec.0.template.0.spec.0.container.0.port.0.container_port
    }
  }
}
