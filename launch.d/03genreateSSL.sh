#!/bin/bash

openssl req -x509 -newkey rsa:2048\
            -keyout ./secrets/ssl.key\
            -out ./secrets/ssl.crt\
            -days 365\
            -nodes -subj "/"

exit 0
