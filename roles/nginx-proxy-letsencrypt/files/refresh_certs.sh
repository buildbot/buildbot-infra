#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"

docker-compose up certbot
docker-compose exec nginx-proxy nginx -s reload
