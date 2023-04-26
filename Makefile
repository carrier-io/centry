INTERFACE ?= lo
REGEX_IFACE := ^[^[:space:]]*:
REGEX_IPV4 := inet \K([0-9]{1,3}[\.]){3}[0-9]{1,3}
IFCONFIG_CMD := /sbin/ifconfig
UID := $(shell id -u)
export UID

SET_IP=$(shell $(IFCONFIG_CMD) $(INTERFACE) | grep -P -o "$(REGEX_IPV4)")
GET_CENTRY_VOLUMES=$(shell docker volume ls -q | grep centry)

.PHONY: all list_interfaces ip fix_permissions up down docker_volumes_prune

all:
	@echo Please read this info carefully for centry to properly work
	@echo ===========================================================
	@echo These recipes will help to run centry locally
	@echo But first some preconfiguration is needed
	@echo ----------------------------------------
	@echo 1. Copy config/pylon-example.yml to config/pylon.yml
	@echo If needed change conifguration in config/pylon.yml
	@echo More in README.md
	@echo ----------------------------------------
	@echo 2. Configure external DEV_IP in .env file
	@echo To do so run \`make list_interfaces\`
	@echo This will show list of interfaces and their corresponding ipv4
	@echo Choose the interface through which you have access
	@echo ------------------------------------------------------------------------
	@echo 3. Run \`make up INTERFACE=\<name_of_the_interface\>\`
	@echo This will setup environment properly and start docker containers

list_interfaces:
	$(IFCONFIG_CMD) | grep -P -o "($(REGEX_IFACE)|$(REGEX_IPV4))"
ip:
	@echo DIRECT_IP = $(DIRECT_IP)
	@echo INTERFACE = $(INTERFACE)
    ifneq ($(DIRECT_IP),)
		@echo  Setting DEV_IP in .env to \`$(DIRECT_IP)\`
		$(eval IP=$(DIRECT_IP))
    else
    ifneq ($(INTERFACE),)
		@echo  Setting DEV_IP in .env with ipv4 for \`$(INTERFACE)\` interface
		$(eval IP=$(SET_IP))
    else
		$(error "It is mandatory to set at least one of DIRECT_IP or INTERFACE environment variables! (e.g. `export INTERFACE=eth0` before calling `make up...`)")
    endif
    endif
	sed -i -e "s+DEV_IP=.*+DEV_IP=$(IP)+g" .env
	@echo DONE with IP=$(IP)

fix_permissions:
	chmod a+rx ./config/extras/postgre_schemas.sh
	chmod a+rx ./config/keycloak/disablessl.sh

config/pylon.yml:
	./configure_pylon.sh

up: fix_permissions ip config/pylon.yml
	docker compose up -d

up_with_custom_CA_cert: fix_permissions ip config/pylon.yml
    ifneq ($(CUSTOM_CA_CERT),)
		@echo Running docker compose with custom CA certificate file: $(CUSTOM_CA_CERT)
		docker compose -f docker-compose.yaml -f docker-compose_custom_CA_cert.yaml up -d
    else
		@echo CUSTOM_CA_CERT environment variable is not set, aborting...
    endif

up_with_mitmproxy: ip
	@(cp ~/.mitmproxy/mitmproxy-ca-cert.pem ./mitmproxy-ca-cert.pem)
	docker compose create
	$(MAKE) mitmproxy_iptables_register
	CUSTOM_CA_CERT=./mitmproxy-ca-cert.pem $(MAKE) up_with_custom_CA_cert

down:
	docker compose down

down_with_mitmproxy: mitmproxy_iptables_remove
	docker compose down

pylon_state_clean:
	rm -rf ./pylon/plugins/*
	rm -rf ./pylon/requirements/*

pylon_auth_state_clean:
	rm -rf ./pylon_auth/plugins/*
	rm -rf ./pylon_auth/requirements/*

pylon_worker_state_clean:
	rm -rf ./pylon_worker/plugins/*
	rm -rf ./pylon_worker/requirements/*

docker_volumes_prune: down
	docker volume rm $(GET_CENTRY_VOLUMES)

clean_all:
	$(MAKE) pylon_state_clean
	$(MAKE) pylon_auth_state_clean
	$(MAKE) pylon_worker_state_clean
	$(MAKE) docker_volumes_prune

docker_system_prune: down
	docker system prune -a --volumes

mitmproxy_interface_show:
	$(IFCONFIG_CMD) | grep -P -o "$(REGEX_IFACE)" | grep -o -P "br-[^:]+"

mitmproxy_iptables_register:
	$(eval IF=$(shell $(IFCONFIG_CMD) | grep -P -o "$(REGEX_IFACE)" | grep -o -P "br-[^:]+"))
	@echo Registering iptable rules to forward all traffic from $(IF) targeting ports 80/443 to mitmproxy...
	@(sudo iptables -t nat -A PREROUTING -i $(IF) -p tcp --dport 80 -j REDIRECT --to-port 8080)
	@(sudo iptables -t nat -A PREROUTING -i $(IF) -p tcp --dport 443 -j REDIRECT --to-port 8080)
	@(sudo ip6tables -t nat -A PREROUTING -i $(IF) -p tcp --dport 80 -j REDIRECT --to-port 8080)
	@(sudo ip6tables -t nat -A PREROUTING -i $(IF) -p tcp --dport 443 -j REDIRECT --to-port 8080)

mitmproxy_iptables_remove:
	$(eval IF=$(shell $(IFCONFIG_CMD) | grep -P -o "$(REGEX_IFACE)" | grep -o -P "br-[^:]+"))
	@echo Removing iptable rules to forward all traffic from $(IF) targeting ports 80/443 to mitmproxy...
	@(sudo iptables -t nat -D PREROUTING -i $(IF) -p tcp --dport 80 -j REDIRECT --to-port 8080)
	@(sudo iptables -t nat -D PREROUTING -i $(IF) -p tcp --dport 443 -j REDIRECT --to-port 8080)
	@(sudo ip6tables -t nat -D PREROUTING -i $(IF) -p tcp --dport 80 -j REDIRECT --to-port 8080)
	@(sudo ip6tables -t nat -D PREROUTING -i $(IF) -p tcp --dport 443 -j REDIRECT --to-port 8080)

mitmproxy_iptables_list:
	@(sudo iptables -t nat -L -v --line-numbers | grep "redir ports 8080")
	@(sudo ip6tables -t nat -L -v --line-numbers | grep "redir ports 8080")

mitmproxy_start_transparent:
	mitmproxy --mode transparent --showhost

mitmdump_start_transparent:
	mitmdump --mode transparent --showhost > mitmlog.log

mitmdump_follow_all:
	tail -f mitmlog.log

mitmdump_follow_TLS_failed:
	tail -f mitmlog.log | grep "TLS handshake failed"

mitmdump_print_TLS_failed:
	cat mitmlog.log | grep "TLS handshake failed"

docker_print_IPs:
	@docker inspect -f '{{.Name}} - {{.Config.Image}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $$(docker ps -q)

mitmproxy_prepare_system:
	@(sudo sysctl -w net.ipv4.ip_forward=1)
	@(sudo sysctl -w net.ipv6.conf.all.forwarding=1)
	@(sudo sysctl -w net.ipv4.conf.all.send_redirects=0)
