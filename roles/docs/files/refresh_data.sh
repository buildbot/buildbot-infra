#!/bin/bash

set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

NEED_UPDATE=0

if [ -d bbdocs/.git ]; then
    pushd bbdocs
    OLD_HEAD=$(git rev-parse HEAD)
    git fetch origin
    git reset --hard origin/master
    NEW_HEAD=$(git rev-parse HEAD)

    if [ "$OLD_HEAD" != "$NEW_HEAD" ]; then
        NEED_UPDATE=1
    fi

    popd
else
    rm -rf bbdocs
    git clone https://github.com/buildbot/bbdocs bbdocs
    NEED_UPDATE=1
fi

pushd build_current

# container may have different user IDs inside
chmod 777 scripts
chmod 777 results
chmod 777 work

OLD_BUILDBOT_CONTENT_DATE=$(cat build_current/results/date 2> /dev/null || echo "no such file")

cp ../bbdocs/add-tracking.py scripts/
sudo docker build -f Dockerfile.build -t nopush/bbdocs .
sudo docker run --rm \
    -v "$(pwd)/scripts:/home/user/scripts" \
    -v "$(pwd)/results:/home/user/results" \
    -v "$(pwd)/work:/home/user/work" \
    nopush/bbdocs /build_docs.sh

NEW_BUILDBOT_CONTENT_DATE=$(cat build_current/results/date 2> /dev/null || echo "no such file")

if [ "$OLD_BUILDBOT_CONTENT_DATE" != "$NEW_BUILDBOT_CONTENT_DATE" ]; then
    rm -rf last_content
    cp -ar results/html last_content
    NEED_UPDATE=1
fi

popd

if [ "$NEED_UPDATE" != "0" ]; then
    # Note that content is mounted to container thus it is not removed.
    rm -rf content/new_html
    cp -ar bbdocs/docs content/new_html
    cp -ar build_current/last_content content/new_html/latest
    if [ -d "content/html" ]; then
        mv content/html content/old_html
    fi
    mv content/new_html content/html
    rm -rf content/old_html
fi
