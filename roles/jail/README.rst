Jail Role
=========

The jail role requires four arguments to be used.

``name``
    The name to use for the jail. This must be the non-fqdn jail's hostname.

``hostname``
    The hostname of the jail.

``jail_debug`` (optional)
    set to true to dump the output of bootstrap script run in the jail

``internet_visible`` (optional)
    set to true to configure externally visible network card

.. note::

   JIDs are assigned automatically.  To address the jail use jail's name, for example::

    $ sudo jexec jailtest sh

Example playbook
----------------

::

    ---
    - name: Jail test
      hosts: servicehosts
      roles:
      - role: jail
        name: jailtest
        hostname: jailtest.buildbot.net
        internet_visible: false
