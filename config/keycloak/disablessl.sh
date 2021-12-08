#!/bin/bash
/opt/jboss/keycloak/bin/kcadm.sh config credentials --server http://localhost/auth --realm master --user carrier
/opt/jboss/keycloak/bin/kcadm.sh update realms/master -s sslRequired=NONE
/opt/jboss/keycloak/bin/kcadm.sh update realms/carrier -s sslRequired=NONE