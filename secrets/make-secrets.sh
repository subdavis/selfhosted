#!/bin/bash

secret_files=(
    "authelia_jwt_secret"
    "authelia_session_secret"
)

for secret in "${secret_files[@]}"
do
  # https://unix.stackexchange.com/questions/230673/how-to-generate-a-random-string
  tr -dc A-Za-z0-9 </dev/urandom | head -c 32 > ./${secret}
done