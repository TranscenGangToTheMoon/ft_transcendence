#!/bin/bash

if [ $# -eq 0 ]; then
    echo "No arguments provided"
    echo "Usage: "
    exit 1
elif [ $# -eq 1 ]; then
    if [ -z "$1" ]; then
        echo "Argument 1 is empty!"
        exit 1
    else
        echo "Case 1"
        ENV_DEFAULT=$1
        if [[ ! -f $ENV_DEFAULT ]]; then
            echo No env file found !
            exit
        fi
    fi
elif [ $# -eq 2 ]; then
    if [ -z "$2" ]; then
        echo "Argument 2 is empty!"
        exit 1
    else
        echo "Case 2"
        ENV_DEFAULT=$1
        ENV_OUTPUT=$2
        if [[ ! -f $ENV_DEFAULT ]]; then
            echo No env file found !
            exit
        fi
        echo -n "" > "$ENV_OUTPUT"
    fi
fi
echo $ENV_OUTPUT
generate_password() {
	echo $(LC_ALL=C ; tr -dc 'A-Za-z0-9!?%' < /dev/urandom | head -c 32)
}

while IFS= read -r line; do
    if [[ ! $line == *"PASSWORD"* ]]; then
        if [ ! -z "$ENV_OUTPUT" ]; then
            echo -e $line >> $ENV_OUTPUT
        fi
    else
        var_name=$(echo "$line" | cut -d '=' -f 1)
        new_pass=$(generate_password)
        new_line=$(sed -n "s|^\($var_name=\).*|\1\"$new_pass\"|p" "$ENV_DEFAULT")
        if [ ! -z "$ENV_OUTPUT" ]; then
            echo $new_line >> "$ENV_OUTPUT"
        else
            sed -i "s|^$var_name=.*|$var_name=\"$new_pass\"|" "$ENV_DEFAULT"
        fi
    fi
done < "$ENV_DEFAULT"

echo "Passwords changed !"
exit 0
