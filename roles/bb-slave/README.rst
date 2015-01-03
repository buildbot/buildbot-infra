bb-slave Role
=============

This role allows to create a Buildbot slave running under supervisor.

Parameters:

``bb_user``
    User to run Buildbot slave under

``bb_slave_name``
    Build slave user.
    It serves several purposes:

    * name to use while authenticating to the build master
    * key in `build_slaves` structure (defined in `secrets.yml`) to get the
      master name and the password to use

``bb_env_dir``
    Virtual environment directory where buildbot-slave is installed.
    Relative to this path `bin/buildslave` will be looked for.

``bb_slave_dir``
    Base directory of the build slave (location of `buildbot.tac` file and work
    directories for builds).
