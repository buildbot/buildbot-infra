Jail Role
=========

The jail role requires four arguments to be used.

``name``
    The name to use for the jail. This is often the same as the hostname.

``hostname``
    The hostname of the jail.

``jid``
    The jail ID. This must be unique on the host.

``ip_address``
    A list of interface and IP address pairs. Each address in the list should be of the form `interface|ip`.


Example playbook
----------------

::

    ---
    - name: Jail test
      hosts: servicehosts
      roles:
        - role: jail
          name: jailtest.buildbot.net
          jid: 1
          hostname: jailtest.buildbot.net
          ip_address: ['vtnet0|192.168.8.49']
