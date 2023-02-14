INTERFACE ?= lo
REGEX_IFACE := ^[^[:space:]]*:
REGEX_IPV4 := inet \K([0-9]{1,3}[\.]){3}[0-9]{1,3}
IFCONFIG_CMD := /sbin/ifconfig
UID := $(shell id -u)
export UID 

SET_IP=$(shell $(IFCONFIG_CMD) $(INTERFACE) | grep -P -o "$(REGEX_IPV4)")
GET_CENTRY_VOLUMES=$(shell docker volume ls -q | grep centry)

.PHONY: all list_interfaces ip fix_permissions up down 
	
all:
	@echo Please read this info carefully for centry to properly work
	@echo ===========================================================
	@echo These recipes will help to run centry locally
	@echo But first some preconfiguration is needed
	@echo ----------------------------------------
	@echo First configure external DEV_IP in .env file
	@echo To do so run \`make list_interfaces\` 
	@echo This will show list of interfaces and their corresponding ipv4
	@echo Choose the interface through which you have access
	@echo \!\! Disable any firewall'('allow all traffic')' rules on this interface
	@echo ------------------------------------------------------------------------
	@echo Secondly run \`make up INTERFACE=\<name_of_the_interface\>\`
	@echo This will setup environment properly and start docker containers

list_interfaces:
	$(IFCONFIG_CMD) | grep -P -o "($(REGEX_IFACE)|$(REGEX_IPV4))"
ip:
	@echo  Setting DEV_IP in .env with ipv4 for \`$(INTERFACE)\` interface
	$(eval IP=$(SET_IP))
	sed -i -e "s+DEV_IP=.*+DEV_IP=$(IP)+g" .env
	@echo DONE with IP=$(IP)

fix_permissions:
	chmod a+rx ./config/extras/postgre_schemas.sh
	chmod a+rx ./config/keycloak/disablessl.sh

config/pylon.yml:
	./configure_pylon.sh

up: fix_permissions ip config/pylon.yml
	docker compose up -d

down:
	docker compose down

purge: down
	docker volume rm $(GET_CENTRY_VOLUMES)

