locals {
  postgres_name = "${var.name_prefix}-postgres"
}


resource "kubernetes_secret" "postgres" {
  metadata {
    name = local.postgres_name
  }
  #
  data = {
    password = var.postgres_password
  }
}


resource "kubernetes_config_map" "postgres" {
  metadata {
    name = local.postgres_name
  }
  #
  data = {
    user        = var.postgres_user
    db          = var.postgres_db
    initdb_args = var.postgres_initdb_args
  }
}


resource "kubernetes_persistent_volume_claim" "postgres" {
  metadata {
    name = local.postgres_name
  }
  #
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = var.postgres_storage
      }
    }
  }
  #
  wait_until_bound = false
}


resource "kubernetes_deployment" "postgres" {
  metadata {
    name = local.postgres_name
    labels = {
      name = local.postgres_name
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
        name = local.postgres_name
      }
    }
    #
    template {
      metadata {
        labels = {
          name = local.postgres_name
        }
      }
      #
      spec {
        container {
          name  = local.postgres_name
          image = "postgres:16.0"
          #
          env {
            name = "POSTGRES_USER"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.postgres.metadata.0.name
                key  = "user"
              }
            }
          }
          env {
            name = "POSTGRES_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.postgres.metadata.0.name
                key  = "password"
              }
            }
          }
          env {
            name = "POSTGRES_DB"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.postgres.metadata.0.name
                key  = "db"
              }
            }
          }
          env {
            name = "POSTGRES_INITDB_ARGS"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.postgres.metadata.0.name
                key  = "initdb_args"
              }
            }
          }
          #
          env {
            name  = "PGDATA"
            value = "/data/pgdata"
          }
          #
          port {
            container_port = 5432
          }
          #
          volume_mount {
            name       = local.postgres_name
            mount_path = "/data"
          }
        }
        volume {
          name = local.postgres_name
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.postgres.metadata.0.name
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


resource "kubernetes_service" "postgres" {
  metadata {
    name = local.postgres_name
  }
  #
  spec {
    selector = {
      name = kubernetes_deployment.postgres.metadata.0.name
    }
    #
    port {
      protocol    = "TCP"
      port        = kubernetes_deployment.postgres.spec.0.template.0.spec.0.container.0.port.0.container_port
      target_port = kubernetes_deployment.postgres.spec.0.template.0.spec.0.container.0.port.0.container_port
    }
  }
}
