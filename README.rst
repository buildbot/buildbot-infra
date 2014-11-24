Ansible
=======

Run ``ansible-playbook -i prod-hosts -s site.yml`` to configure the production site.

Development
-----------

During development, you may create a ``dev-hosts`` file containing your test hosts.
Then run ``ansible-playbook -s site.yml`` to test your changes.

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

-  buildbot.asc - Buildbot Release Team Keyring
-  scripts/ - some scripts not under configuration management yet
