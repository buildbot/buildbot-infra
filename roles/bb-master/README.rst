Buildbot Master Role
====================

This role allows to get an instance of the Buildbot master as defined in
https://github.com/buildbot/metabbotcfg

Parameters:

``bb_user``
    User to run Buildbot master under

``bb_user_home``
    Home directory of the above user (used to create a checkout of buildbot.git
    repository)

``bb_branch``
    Branch of buildbot.git to be deployed

``bb_config_branch``
    Branch of metabbotcfg.git to be deployed

``bb_env_dir``
    Virtual environment to install the master to (must be prepared before
    trying the installation of the build master)

``bb_master_dir``
    Directory where the master will be created (location of master.cfg).

``bb_service``
    Name of the supervisor service for this build master (used to stop and
    start it when an update takes place)
