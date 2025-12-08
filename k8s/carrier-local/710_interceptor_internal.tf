locals {
  interceptor_internal_name = "${var.name_prefix}-interceptor-internal"
}


resource "kubernetes_deployment" "interceptor_internal" {
  metadata {
    name = local.interceptor_internal_name
    labels = {
      name = local.interceptor_internal_name
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
        name = local.interceptor_internal_name
      }
    }
    #
    template {
      metadata {
        labels = {
          name = local.interceptor_internal_name
        }
      }
      #
      spec {
        container {
          name              = local.interceptor_internal_name
          image             = "getcarrier/interceptor:test"
          image_pull_policy = "IfNotPresent"
          #
          env {
            name  = "SUPERVISOR_CONF_PATH"
            value = "/tmp/interceptor.conf"
          }
          #
          env {
            name  = "SSL_CERTS"
            value = "/cacerts"
          }
          env {
            name  = "SSL_VERIFY"
            value = "yes"
          }
          #
          env {
            name  = "EXECUTOR_RUNTIME"
            value = "kubernetes"
          }
          env {
            name  = "K8S_MOUNT_TMP"
            value = "yes"
          }
          env {
            name  = "K8S_STOP_JOBS"
            value = "yes"
          }
          #
          env {
            name  = "CPU_CORES"
            value = var.interceptor_internal_cpu_cores
          }
          #
          env {
            name  = "QUEUE_NAME"
            value = "__internal"
          }
          #
          env {
            name  = "ARBITER_RUNTIME"
            value = "redis"
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
          volume_mount {
            name       = "${local.interceptor_internal_name}-cacerts"
            mount_path = "/cacerts"
            read_only  = true
          }
        }
        #
        volume {
          name = "${local.interceptor_internal_name}-cacerts"
          config_map {
            name = kubernetes_config_map.cacerts.metadata.0.name
          }
        }
        #
        restart_policy                   = "Always"
        termination_grace_period_seconds = 30
        #
        service_account_name = kubernetes_service_account.interceptor.metadata.0.name
      }
    }
  }
  #
  wait_for_rollout = false
}
