#!/bin/bash

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

if [ "$NEED_UPDATE" != "0" ]; then
    # Note that content is mounted to container thus it is not removed.
    rm -rf content/{*,.*}
    cp -ar bbdocs/docs/* content
fi
