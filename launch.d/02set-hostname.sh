#!/bin/bash
ENV_DEFAULT="srcs/.env"

CURRENT_HOSTNAME=$(hostname)

if grep -q "^HOSTNAME=" "$ENV_DEFAULT"; then
  sed -i "s/^HOSTNAME=.*/HOSTNAME=$CURRENT_HOSTNAME/" "$ENV_DEFAULT"
  echo "HOSTNAME changed!"
else
  echo "HOSTNAME=$CURRENT_HOSTNAME" >> "$ENV_DEFAULT"
  echo "HOSTNAME added!"
fi


exit 0
