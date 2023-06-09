#!/bin/bash

sleep 60
/opt/jboss/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080/auth --realm master --user $KU --password $KP
/opt/jboss/keycloak/bin/kcadm.sh update realms/master -s sslRequired=NONE
/opt/jboss/keycloak/bin/kcadm.sh update realms/carrier -s sslRequired=NONE