#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"

docker-compose up certbot
docker-compose exec -T nginx-proxy nginx -s reload
