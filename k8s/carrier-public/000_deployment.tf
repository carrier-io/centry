resource "kubernetes_config_map" "deployment" {
  metadata {
    name = "${var.name_prefix}-deployment"
  }
  #
  data = {
    app_proto = var.deployment_app_proto
    app_host  = var.deployment_app_host
  }
}


resource "kubernetes_secret" "deployment" {
  metadata {
    name = "${var.name_prefix}-deployment"
  }
  #
  data = {
    rpc_hmac_key      = var.deployment_rpc_hmac_key
    event_hmac_key    = var.deployment_event_hmac_key
    exposure_hmac_key = var.deployment_exposure_hmac_key
  }
}


resource "kubernetes_secret" "license" {
  metadata {
    name = "${var.name_prefix}-license"
  }
  data = {
    username = var.license_username
    password = var.license_password
  }
}


resource "kubernetes_manifest" "backendconfig" {
  manifest = {
    "apiVersion" = "cloud.google.com/v1"
    "kind"       = "BackendConfig"
    "metadata" = {
      "name"      = "${var.name_prefix}-backendconfig"
      "namespace" = "default"
    }
    "spec" = {
      "timeoutSec" = var.backendconfig_timeout
    }
  }
}


locals {
  cacerts_data = "${path.module}/data/cacerts"
}


resource "kubernetes_config_map" "cacerts" {
  metadata {
    name = "${var.name_prefix}-cacerts"
  }
  #
  data = {
    for item in fileset(local.cacerts_data, "**") :
    item => file(join("/", [local.cacerts_data, item]))
  }
}
