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
Before running the script, ensure:

* The basic system is installed (FreeBSD 10.0+) on the host
* Networking for the host is fully configured
* The hostname (uname -n) of the host is set correctly
* The root password is known (or SSH keys set up)
* Ssh access for 'root' is enabled (`PermitRootLogin yes`; note that this is not the default!)
* You know the vault password

Development
-----------

Development is made easier with Vagrant.

First install 3 vagrant box with FreeBSD 10.3. Each of them representing one of the hw hosts::

    vagrant up

Those vagrant boxes will be used to host all jails as it is in prod.
``vagrant up`` will run the ansible script for all those 3 boxes, and create all the jails.
The jails will not be fully provisionned though (they only will be provisionned with ssh and vagrant user).
You need to run ansible on each of those jails to actually activate the services

Internal network is mapped to the virtualbox host's network, so you can connect to the jails using their ip address.

Difference between prod are:
- sshd is enabled in jails
- a ``vagrant`` user is added in jail, which can be connected using the identity file that vagrant generated to create the host (.vagrant/machines/<host>/virtualbox/private_key)
- connection is over ssh
- ansible-pull is disabled
- keep only internal network ip addresses

To setup all jails on your dev system just run::

    ansible-playbook --vault-password=~/.vault-password -i vagrant_inventory.py vagrant.yml

But it is preferable to only run ansible for the jail you are working on::

    ansible-playbook --vault-password=~/.vault-password -i vagrant_inventory.py vagrant.yml -l ns1

vagrant_inventory.py will automatically figure out which jail needs to be connected to, and with which ssh key

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
