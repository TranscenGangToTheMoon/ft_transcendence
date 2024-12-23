#!/bin/bash

openssl req -x509 -newkey rsa:2048\
            -keyout ./secrets/ssl.key\
            -out ./secrets/ssl.crt\
            -days 365\
            -nodes\
            -subj "/C=FR/ST=Auvergne-Rhone-Alpes/L=Lyon/O=42Lyon/CN=localhost"\
            -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
exit 0
