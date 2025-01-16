#!/bin/bash

echo "[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = FR
ST = Auvergne-Rhone-Alpes
L = Lyon
O = 42Lyon
CN = localhost

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = $(hostname)" > secrets/ssl.conf

echo "IP.1 = 127.0.0.1" >> secrets/ssl.conf

counter=2

# Ajouter toutes les IPs locales (fonctionne sur Linux et macOS)
for ip in $(hostname -I 2>/dev/null || ipconfig getifaddr en0 2>/dev/null); do
    echo "IP.$counter = $ip" >> secrets/ssl.conf
    counter=$((counter+1))
done

openssl req -x509 -newkey rsa:2048\
            -keyout ./secrets/ssl.key\
            -out ./secrets/ssl.crt\
            -days 365\
            -nodes\
            -config secrets/ssl.conf
exit 0
