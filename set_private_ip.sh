#!/bin/bash

# Get EC2 private IP using IMDSv2
TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
PRIVATE_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/local-ipv4)

if [ -z "$PRIVATE_IP" ]; then
  echo "Failed to retrieve private IP. Exiting."
  exit 1
fi

# Replace APP_IP in .env
if [ -f .env ]; then
  sed -i "s/^APP_IP=.*/APP_IP=$PRIVATE_IP/" .env
  echo ".env updated: APP_IP=$PRIVATE_IP"
else
  echo ".env file not found!"
fi

# Replace DIRECT_IP in Makefile
if [ -f Makefile ]; then
  sed -i "s/^DIRECT_IP=.*/DIRECT_IP=$PRIVATE_IP/" Makefile
  echo "Makefile updated: DIRECT_IP=$PRIVATE_IP"
else
  echo "Makefile not found!"
fi