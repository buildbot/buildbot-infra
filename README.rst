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

Development
-----------

Development is made easier with Vagrant.

First install 3 vagrant box with FreeBSD 10.3. Each of them representing one of the hw hosts::

    vagrant up

Those vagrant boxes will be used to host all jails as it is in prod.
``vagrant up`` will run the Ansible script for all those 3 boxes, and create all the jails.
The jails will not be fully provisioned though (they only will be provisioned with ssh and vagrant user).
You need to run Ansible on each of those jails to actually activate the services.

Internal network is mapped to the virtualbox host's network, so you can connect to the jails using their ip address.

Difference between prod are:

- sshd is enabled in jails
- a ``vagrant`` user is added in jail, which can be connected using the identity file that vagrant generated to create the host (``.vagrant/machines/<host>/virtualbox/private_key``)
- connection is over ssh
- ``ansible-pull`` is disabled
- keep only internal network ip addresses

To setup all jails on your dev system just run:

.. code-block:: bash

    ansible-playbook --vault-password=~/.vault-password -i vagrant_inventory.py vagrant.yml

But it is preferable to only run Ansible for the jail you are working on:

.. code-block:: bash

    ansible-playbook --vault-password=~/.vault-password -i vagrant_inventory.py vagrant.yml -l ns1

``vagrant_inventory.py`` will automatically figure out which jail needs to be connected to, and with which ssh key

To use development secrets (which may be unencrypted), create ``dev-secrets.yml`` and invoke Ansible with ``-e secrets_file=dev-secrets.yml``.

Development with proxies
------------------------

Because of https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=212452 the vagrant boostrap will not work when your environment requires http proxies to access internet.

In that case, during VM creation phase, vagrant will indefinitly try to connect via ssh.

- You need to attach to the VM using virtualbox UI, and go to the freebsd console.
- Hit CTRL-C will stop the firstboot script and give you login prompt
- Use ``root:vagrant``  as ``login:password``
- Type following in the console:

    .. code-block:: bash

        setenv http_proxy http://xxx
        pkg install -y sudo

- then you can run ``vagrant provision`` again

You need to do this setup for the three hosts VMs.
Once this is done the environment variables ``http_proxy``, ``https_proxy``, and ``https_proxy`` are copied inside the Ansible run for the commands that needs internet access.

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
