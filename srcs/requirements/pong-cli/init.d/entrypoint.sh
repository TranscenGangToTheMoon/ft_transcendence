#!/bin/bash
RED="\001\033[031m\002"
BOLD="\001\033[001m\002"
RESET="\001\033[000m\002"

git clone --depth 1 --branch v5.0.0 https://github.com/ArthurSonzogni/ftxui
cd ftxui
cmake -B build .
cd build && make
make install
cd /
rm -rf ftxui

exec "$@"