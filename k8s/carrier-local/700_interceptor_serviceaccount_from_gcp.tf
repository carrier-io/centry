resource "kubernetes_service_account" "interceptor" {
  metadata {
    name = "interceptor"
  }
}


resource "kubernetes_role" "interceptor" {
  metadata {
    name = "interceptor"
  }
  #
  rule {
    api_groups = ["batch"]
    resources  = ["jobs"]
    verbs      = ["create", "delete"]
  }
  rule {
    api_groups = ["batch"]
    resources  = ["jobs/status"]
    verbs      = ["get"]
  }
  #
  rule {
    api_groups = [""]
    resources  = ["pods"]
    verbs      = ["list"]
  }
  rule {
    api_groups = [""]
    resources  = ["pods/log"]
    verbs      = ["get"]
  }
}


resource "kubernetes_role_binding" "interceptor" {
  metadata {
    name = "interceptor"
  }
  #
  subject {
    kind = "ServiceAccount"
    name = kubernetes_service_account.interceptor.metadata.0.name
  }
  #
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.interceptor.metadata.0.name
  }
}
