#! /bin/sh

set -e

dir="${1}"
commit_message="${2}"

if ! [ -d "${dir}" ]; then
    # nothing to track
    exit 0
fi
cd "${dir}"

if ! [ -d ".git" ]; then
    git init
fi

# unconditionally update the config as necessary
git config user.email "{{ track_config['default_author_email'] }}"
git config user.name "{{ track_config['default_author_name'] }}"

# check for changes
if git status 2>/dev/null | grep -q 'working directory clean'; then
    exit 0
fi

# use git add --all to capture deletes, too
git add --all .

# commit the changes
git commit --author='{{ track_config['author_name'] }} <{{ track_config['author_email'] }}>' \
    -m "${commit_message}"
