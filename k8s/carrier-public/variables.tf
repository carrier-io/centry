variable "project_id" {
  type = string
}

variable "region" {
  type = string
}


variable "cluster_name" {
  type = string
}

variable "ip_name" {
  type = string
}


variable "ssl_cert_name" {
  type = string
}


variable "name_prefix" {
  type = string
}

variable "default_admin_password" {
  type = string
}


variable "deployment_app_proto" {
  type = string
}

variable "deployment_app_host" {
  type = string
}


variable "deployment_rpc_hmac_key" {
  type = string
}

variable "deployment_event_hmac_key" {
  type = string
}

variable "deployment_exposure_hmac_key" {
  type = string
}


variable "license_username" {
  type = string
}

variable "license_password" {
  type = string
}


variable "backendconfig_timeout" {
  type = number
}


variable "redis_password" {
  type = string
}

variable "redis_storage" {
  type = string
}

variable "redis_storage_class" {
  type = string
}

variable "influx_storage" {
  type = string
}

variable "influx_storage_class" {
  type = string
}


variable "postgres_db" {
  type = string
}

variable "postgres_user" {
  type = string
}

variable "postgres_password" {
  type = string
}

variable "postgres_initdb_args" {
  type = string
}

variable "postgres_storage" {
  type = string
}

variable "postgres_storage_class" {
  type = string
}


variable "pylon_auth_application_secret_key" {
  type = string
}

variable "pylon_auth_storage" {
  type = string
}

variable "pylon_auth_storage_class" {
  type = string
}


variable "pylon_main_application_secret_key" {
  type = string
}

variable "pylon_main_secrets_master_key" {
  type = string
}

variable "pylon_main_storage" {
  type = string
}

variable "pylon_main_storage_class" {
  type = string
}


variable "interceptor_internal_cpu_cores" {
  type = string
}


variable "interceptor_cpu_cores" {
  type = string
}

variable "interceptor_ram_quota" {
  type = string
}

variable "interceptor_cpu_quota" {
  type = string
}

variable "interceptor_platform_auth_token" {
  type = string
}
