#!/bin/bash

set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

mkdir -p build_current
pushd build_current

# container may have different user IDs inside
mkdir -p results
mkdir -p work
chmod 777 results
chmod 777 work

OLD_BUILDBOT_CONTENT_DATE=$(cat results/date 2> /dev/null || echo "no such file")

sudo docker build -f Dockerfile.build -t nopush/nginx-buildbot-www-build .
sudo docker run --rm \
    -v "$(pwd)/results:/home/user/results" \
    -v "$(pwd)/work:/home/user/work" \
    nopush/nginx-buildbot-www-build /build_www.sh

NEW_BUILDBOT_CONTENT_DATE=$(cat results/date 2> /dev/null || echo "no such file")

if [ "$OLD_BUILDBOT_CONTENT_DATE" != "$NEW_BUILDBOT_CONTENT_DATE" ]; then
    rm -rf last_content
    cp -ar results/html last_content
    NEED_UPDATE=1
fi

popd

if [ "$NEED_UPDATE" != "0" ]; then
    # Note that content is mounted to container thus it is not removed.
    rm -rf content/new_html
    cp -ar build_current/last_content content/new_html

    # Use mv to swap data quickly
    if [ -d "content/html" ]; then
        mv content/html content/old_html
    fi
    mv content/new_html content/html
    rm -rf content/old_html
fi
