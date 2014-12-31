Simple Buildout Role
====================

This role allows to maintain an up to date working copy of the specified repository and perform a "build" when it changes.

Parameters:

``repo_url``
    URL of the git repository to watch.

``repo_branch``
    Use the particular branch of the repo above.

``target_user``
    User to perform the operations under.

``target_dir``
    Absolute path for the working copy directory.

``target_commands`` (optional, default -- empty list)
    A list of commands suitable for `command` module.

Example::

    ...
    - role: simple-buildout
      repo_url: git://github.com/buildbot/buildbot-website.git
      repo_dir: site
      repo_commands:
      - "npm install"
      - "./node_modules/.bin/grun prod"
