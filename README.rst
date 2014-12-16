Ansible
=======

Production Runs
---------------

Production runs of Ansible take place on the host or jail to be configured, as the ``{{service_user}}``, with a command line such as ::

    ansible-playbook local.yml

This playbook automatically determines which host it's runnning on based on the hostname and configures it accordingly.
Supply host-specific variables in ``group_vars/$hostname``.

Bootstrapping
-------------

To bootstrap a newly-installed system, use ``./bootstrap HOSTNAME``.
Before running the script, ensure:

* The basic system is installed (FreeBSD 10.0+) on the host
* Networking for the host is fully configured
* The hostname (uname -n) of the host is set correctly
* The root password is known (or SSH keys set up)
* Ssh access for 'root' is enabled (`PermitRootLogin yes`; note that this is not the default!)
* You know the vault password

Development
-----------

To develop a patch on a test system, set the system's base hostname to correspond to the host or jail you want to work on, and run the same command::

    ansible-playbook local.yml

To avoid installing the Ansible crontask, add ``-e no_ansible_pull=true``.

To use development secrets (which may be unencrypted), create ``dev-secrets.yml`` and invoke Ansible with ``-e secrets_file=dev-secrets.yml``.

Secrets
-------

Secrets are stored in ``secrets.yml`` in the top-level directory, which is encrypted with `ansible-vault <http://docs.ansible.com/playbooks_vault.html>`__.
To run Ansible with these production secrets, you will need to supply a shared vault password.

All secrets are loaded into Ansible variables.
By convention, these variables should be named with the prefix ``secret_``.

You can edit the secrets with ``ansible-vault edit secrets.yml``.

Other files
===========

This repository contains a few files unrelated to Ansible:

-  buildbot.asc - Buildbot Release Team Keyring
-  scripts/ - some scripts not under configuration management yet
