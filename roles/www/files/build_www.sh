#!/bin/bash

set -e

ROOTDIR=/home/user
cd "$ROOTDIR/work"

NEED_UPDATE=0

if [ -d buildbot-website/.git ]; then
    pushd buildbot-website
    git fetch origin
    git reset --hard origin/master

    OLD_HEAD=$(cat "$ROOTDIR/results/commit" || echo "no commit")
    NEW_HEAD=$(git rev-parse HEAD)

    if [ "$OLD_HEAD" != "$NEW_HEAD" ]; then
        NEED_UPDATE=1
    fi

    popd
else
    rm -rf buildbot-website
    git clone https://github.com/buildbot/buildbot-website buildbot-website
    NEW_HEAD=$(cd buildbot-website && git rev-parse HEAD)
    NEED_UPDATE=1
fi

if [ "$NEED_UPDATE" = "0" ]; then
    echo "Skipped"
    exit 0
fi

pushd buildbot-website
yarnpkg install --pure-lockfile
yarnpkg run compile

rm -rf "$ROOTDIR/results/html"
rm -rf "$ROOTDIR/results/date"
rm -rf "$ROOTDIR/results/commit"
cp -ar dist "$ROOTDIR/results/html"
date --iso-8601=ns > "$ROOTDIR/results/date"
echo "$NEW_HEAD" > "$ROOTDIR/results/commit"

echo "Done"
