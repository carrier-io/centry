locals {
  pylon_auth_name    = "${var.name_prefix}-pylon-auth"
  pylon_auth_configs = "${path.module}/data/configs/pylon_auth"
}


resource "kubernetes_secret" "pylon_auth" {
  metadata {
    name = local.pylon_auth_name
  }
  #
  data = {
    application_secret_key = var.pylon_auth_application_secret_key
  }
}


resource "kubernetes_persistent_volume_claim" "pylon_auth" {
  metadata {
    name = local.pylon_auth_name
  }
  #
  spec {
    access_modes       = ["ReadWriteOnce"]
    storage_class_name = var.pylon_auth_storage_class
    resources {
      requests = {
        storage = var.pylon_auth_storage
      }
    }
  }
  #
  wait_until_bound = false
}


resource "kubernetes_config_map" "pylon_auth" {
  metadata {
    name = local.pylon_auth_name
  }
  #
  data = {
    for item in fileset(local.pylon_auth_configs, "*") :
    item => file(join("/", [local.pylon_auth_configs, item]))
  }
}


resource "kubernetes_deployment" "pylon_auth" {
  metadata {
    name = local.pylon_auth_name
    labels = {
      name = local.pylon_auth_name
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
        name = local.pylon_auth_name
      }
    }
    #
    template {
      metadata {
        labels = {
          name = local.pylon_auth_name
        }
      }
      #
      spec {
        container {
          name              = local.pylon_auth_name
          image             = "getcarrier/pylon:tasknode"
          image_pull_policy = "Always"
          #
          env {
            name  = "PYLON_WEB_RUNTIME"
            value = "gevent"
          }
          env {
            name  = "PYLON_CONFIG_SEED"
            value = "file:/config/pylon.yml"
          }
          #
          env {
            name  = "NAME"
            value = local.pylon_auth_name
          }
          env {
            name  = "NAME_PREFIX"
            value = var.name_prefix
          }
          #
          env {
            name  = "DEFAULT_ADMIN_PASSWORD"
            value = var.default_admin_password
          }
          #
          env {
            name = "APPLICATION_SECRET_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.pylon_auth.metadata.0.name
                key  = "application_secret_key"
              }
            }
          }
          #
          env {
            name = "APP_PROTO"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.deployment.metadata.0.name
                key  = "app_proto"
              }
            }
          }
          env {
            name = "APP_HOST"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.deployment.metadata.0.name
                key  = "app_host"
              }
            }
          }
          #
          env {
            name = "RPC_HMAC_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.deployment.metadata.0.name
                key  = "rpc_hmac_key"
              }
            }
          }
          env {
            name = "EVENT_HMAC_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.deployment.metadata.0.name
                key  = "event_hmac_key"
              }
            }
          }
          env {
            name = "EXPOSURE_HMAC_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.deployment.metadata.0.name
                key  = "exposure_hmac_key"
              }
            }
          }
          #
          env {
            name  = "REDIS_HOST"
            value = kubernetes_service.redis.metadata.0.name
          }
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
          env {
            name  = "POSTGRES_HOST"
            value = kubernetes_service.postgres.metadata.0.name
          }
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
          #
          env {
            name = "LICENSE_USERNAME"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.license.metadata.0.name
                key  = "username"
              }
            }
          }
          env {
            name = "LICENSE_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.license.metadata.0.name
                key  = "password"
              }
            }
          }
          #
          port {
            container_port = 8080
          }
          #
          readiness_probe {
            http_get {
              path = "/readyz"
              port = 8080
            }
            initial_delay_seconds = 15
            period_seconds        = 10
          }
          #
          volume_mount {
            name       = local.pylon_auth_name
            mount_path = "/data"
          }
          volume_mount {
            name       = "${local.pylon_auth_name}-config"
            mount_path = "/config"
            read_only  = true
          }
          volume_mount {
            name       = "${local.pylon_auth_name}-cacerts"
            mount_path = "/cacerts"
            read_only  = true
          }
        }
        #
        volume {
          name = local.pylon_auth_name
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.pylon_auth.metadata.0.name
          }
        }
        volume {
          name = "${local.pylon_auth_name}-config"
          config_map {
            name = kubernetes_config_map.pylon_auth.metadata.0.name
          }
        }
        volume {
          name = "${local.pylon_auth_name}-cacerts"
          config_map {
            name = kubernetes_config_map.cacerts.metadata.0.name
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
