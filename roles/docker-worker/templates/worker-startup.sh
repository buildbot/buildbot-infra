#! /bin/bash

# See https://github.com/buildbot/metabbotcfg/blob/master/docker/linux-startup.sh

# startup script for the `linux` worker, which is composed of two DB containers
# and a (customized) worker container.  All DB names, users, and paswords are 'bbtest'.
# That's OK because access to the DB's is limited by docker linking.

set -e

stop() {
    docker stop $1 || true
    docker rm $1 || true
}

stop bbtest-postgres
stop bbtest-mysql
stop bbtest

docker run -d --name bbtest-postgres \
    -e POSTGRES_USER=bbtest \
    -e POSTGRES_PASSWORD=bbtest \
    postgres:9.5

docker run -d --name bbtest-mysql \
    -e MYSQL_RANDOM_ROOT_PASSWORD=1 \
    -e MYSQL_DATABASE=bbtest \
    -e MYSQL_USER=bbtest \
    -e MYSQL_PASSWORD=bbtest \
    buildbot/metamysql:5.6 --character-set-server=utf8 --collation-server=utf8_general_ci 

docker run -d --name bbtest \
    -e BUILDMASTER={{ build_slaves[bb_slave_name].master }} \
    -e BUILDMASTER_PORT=9989 \
    -e WORKERNAME={{ bb_slave_name }} \
    -e WORKERPASS={{ build_slaves[bb_slave_name].password }} \
    --link bbtest-mysql:mysql \
    --link bbtest-postgres:postgresql \
    -d buildbot/metaworker:latest
