project_id = "or2-msq-epm-tigr-t1iylu"
region     = "us-central1"

cluster_name = "autopilot-cluster-public"
ip_name      = "gke-public"

ssl_cert_name = "centry-cert"

name_prefix = "carrier"

default_admin_password = "changeme_admin_password"

deployment_app_proto = "https"
deployment_app_host  = "public.getcarrier.io"

deployment_rpc_hmac_key      = "changeme_deployment_rpc_hmac_key"
deployment_event_hmac_key    = "changeme_deployment_event_hmac_key"
deployment_exposure_hmac_key = "changeme_deployment_exposure_hmac_key"

license_username = ""
license_password = ""

backendconfig_timeout = 86400

redis_password      = "changeme_redis_password"
redis_storage       = "10Gi"
redis_storage_class = "premium-rwo"

influx_storage       = "20Gi"
influx_storage_class = "premium-rwo"

postgres_db            = "carrier_db"
postgres_user          = "carrier"
postgres_password      = "changeme_postgres_password"
postgres_initdb_args   = "--data-checksums"
postgres_storage       = "50Gi"
postgres_storage_class = "premium-rwo"

pylon_auth_application_secret_key = "changeme_auth_application_secret_key"
pylon_auth_storage                = "10Gi"
pylon_auth_storage_class          = "premium-rwo"

pylon_main_application_secret_key = "changeme_main_application_secret_key"
pylon_main_secrets_master_key     = "changeme_pylon_main_secrets_master_key" # docker run --rm --entrypoint= getcarrier/pylon:tasknode python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
pylon_main_storage                = "50Gi"
pylon_main_storage_class          = "premium-rwo"

interceptor_internal_cpu_cores = "15"

interceptor_cpu_cores           = "5"
interceptor_ram_quota           = "4g"
interceptor_cpu_quota           = "1"
interceptor_platform_auth_token = "changeme_interceptor_token"
