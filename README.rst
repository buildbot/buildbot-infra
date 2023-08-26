Ansible
=======

Production Runs
---------------

Production runs of Ansible take place on the host or jail to be configured, as the ``{{service_user}}``, with a command line such as ::

    ansible-playbook local.yml --vault-password=~/.vault-password


This playbook automatically determines which host it's runnning on based on the hostname and configures it accordingly.
Supply host-specific variables in ``group_vars/$hostname``.

Bootstrapping
-------------

To bootstrap a newly-installed system, use ``./bootstrap HOSTNAME``.
Default is to log in to the remote system using your current username.
To change the remote login, use ``./bootstrap HOSTNAME USERNAME``.
Before running the script, ensure:

* The basic system is installed (FreeBSD 10.0+) on the host
* Networking for the host is fully configured
* The hostname (uname -n) of the host is set correctly
* Sudo configured for a non-root user to become root
* You know the vault password

Secrets
-------

Secrets are stored in ``secrets.yml`` in the top-level directory, which is encrypted with `ansible-vault <http://docs.ansible.com/playbooks_vault.html>`__.
To run Ansible with these production secrets, you will need to supply a shared vault password.

All secrets are loaded into Ansible variables.
By convention, these variables should be named with the prefix ``secret_``.

You can edit the secrets with ``ansible-vault --vault-password=~/.vault-password edit secrets.yml``.

Other files
===========

This repository contains a few files unrelated to Ansible:

-  ``buildbot.asc`` - Buildbot Release Team Keyring
-  ``scripts/`` - some scripts not under configuration management yet
