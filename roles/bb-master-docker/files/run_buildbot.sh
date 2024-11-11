#!/bin/bash

BB_SECRETS_ROOT=/home/bbuser/secrets/buildbot
OTHER_SECRETS_ROOT=/home/bbuser/secrets/other
cd /home/bbuser/workdir

cp -t metabbotcfg $BB_SECRETS_ROOT/*

until /home/bbuser/buildbot_venv/bin/buildbot upgrade-master . ; do
    echo "Could not upgrade Buildbot"
    sleep 1
done

gcloud auth activate-service-account \
    $(cat "$OTHER_SECRETS_ROOT/gke_buildbot_master_key_client_email.pass") \
    --key-file "$OTHER_SECRETS_ROOT/buildbot-master.json"

gcloud container clusters get-credentials metabuildbot-fr \
    --zone europe-west9-b \
    --project $(cat "$OTHER_SECRETS_ROOT/gke_project.pass")

exec /home/bbuser/buildbot_venv/bin/twistd --pidfile= -ny buildbot.tac
