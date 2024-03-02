#!/bin/bash

set -e

ROOTDIR=/home/user
cd "$ROOTDIR/work"

NEED_UPDATE=0

if [ -d buildbot/.git ]; then
    pushd buildbot
    OLD_HEAD=$(git rev-parse HEAD)
    git fetch origin
    git reset --hard origin/master
    NEW_HEAD=$(git rev-parse HEAD)

    if [ "$OLD_HEAD" != "$NEW_HEAD" ]; then
        NEED_UPDATE=1
    fi

    popd
else
    rm -rf buildbot
    git clone https://github.com/buildbot/buildbot buildbot
    NEED_UPDATE=1
fi

if [ "$NEED_UPDATE" = "0" ]; then
    echo "Skipped"
    exit 0
fi

pushd buildbot
rm -rf ../venv
python3 -m venv ../venv
source ../venv/bin/activate
pip install -r requirements-cidocs.txt -e master

LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 make -C master/docs VERSION=latest

find master/docs/_build/html -name '*.html' -exec python3 "$ROOTDIR/scripts/add-tracking.py" '{}' \;

rm -rf "$ROOTDIR/results/html"
rm -rf "$ROOTDIR/results/date"
cp -ar master/docs/_build/html "$ROOTDIR/results/html"
date --iso-8601=ns > "$ROOTDIR/results/date"

echo "Done"
