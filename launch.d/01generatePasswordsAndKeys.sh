#!/bin/bash
ENV_DEFAULT=.env_exemple
ENV_OUTPUT=srcs/.env

generate_password() {
    export LC_ALL=C
    echo $(LC_CTYPE=C; tr -dc 'A-Za-z0-9!?%' < /dev/urandom | head -c 32)
}

generate_secret_key() {
    python3 - << EOF
import secrets
length = 50
chars = 'abcdefghijklmnopqrstuvwxyz0123456789%^&*(-_=+)'
secret_key = ''.join(secrets.choice(chars) for i in range(length))
print(secret_key)
EOF
}

# Assurons-nous que le fichier de sortie est vide avant de commencer
> "$ENV_OUTPUT"

while IFS= read -r line; do
    if [[ $line == *"PASSWORD"* ]]; then
        variable=$(echo "$line" | cut -d '=' -f 1)
        password=$(generate_password)
        echo "$variable=\"$password\"" >> "$ENV_OUTPUT"
    elif [[ $line == *"SECRET_KEY"* ]]; then
        variable=$(echo "$line" | cut -d '=' -f 1)
        key=$(generate_secret_key)
        echo "$variable=\"$key\"" >> "$ENV_OUTPUT"
    else
        echo "$line" >> "$ENV_OUTPUT"
    fi
done < "$ENV_DEFAULT"

exit 0
