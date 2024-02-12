# centry
Carrier Platform

## Deployment
### Requirements:
* docker, installed according to [official installation guide](https://docs.docker.com/engine/install/)
* docker compose (e.g. docker-compose-plugin as a part of official installation guide)
* Ports used (start by exposing 80 and 443 on firewall, other ports may be needed to trigger/run scans from remote locations):
    * 80
    * 443
    * 5672
    * 15672
    * 5432
    * 8200
    * 9000
    * 8086
    * 8081
    * 3100

### Configuration:
* Edit `.env`:
  * Set `APP_IP` to your application domain name or IP (e.g. carrier.my-deployment.url.domain)
  * Change passwords from `changeme` to something more secure
* Replace `config/traefik/config/certs/{cert.pem,key.pem}` with your SSL certificate and private key
* _Optionally_: edit `config/pylon_auth.yml` to enable custom SSO (in `auth_oidc` section)

### Run:
* Run `docker compose up -d`
* Watch pylon logs with `docker compose logs -f pylon pylon_main`
