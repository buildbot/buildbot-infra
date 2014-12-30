Jail Role
=========

The jail role requires four arguments to be used.

``name``
    The name to use for the jail. This is often the non-fqdn jail's hostname.

``hostname``
    The hostname of the jail.

``ip_address``
    A list of interface and IP address pairs. Each address in the list should be of the form `interface|ip`.

``jail_debug`` (optional)
    set to true to dump the output of bootstrap script run in the jail

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
        ip_address:
        - 'vtnet0|192.168.8.49'
