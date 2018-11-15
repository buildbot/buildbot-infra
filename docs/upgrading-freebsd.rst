Notes For Upgrading FreeBSD
===========================

This is based on the FreeBSD Handbook, sections 23.2 FreeBSD Update and 14.6.4 Updating Jails.

Process for upgrading a host:

1. Upgrade host.
2. Upgrade host packages.
3. Upgrade basejail userland.
4. Upgrade each jail's etc.
5. Upgrade each jail's packages.


Upgrade Using freebsd-update
----------------------------
Run ``freebsd-update`` as many times as necessary.
At the end of each install will be a note on whether it's necessary to run ``freebsd-update`` again after a reboot.

Minor Upgrade
-------------
For a minor upgrade, such as 11.2-RELEASE-p1 to 11.2-RELEASE-p2, use fetch and install::

    freebsd-update fetch
    freebsd-update install

Major Upgrade
-------------
For a major upgrade, such as 11.2-RELEASE to 11.3-RELEASE or 12.0-RELEASE, use upgrade::

    freebsd-update -r DESTINATION_VERSION upgrade

When the upgrade finishes, you will be instructed to reboot and run ``freebsd-update install``.
Each install may require additional installs after another reboot.

Upgrade Host Packages
---------------------

::

    pkg upgrade

Upgrade basejail's Userland
---------------------------

Use ``ezjail-admin update`` to upgrade the basejail.
The value for the ``-s`` option is the current FreeBSD version of the basejail.

::

    ezjail-admin update -U -s BASEJAIL_CURRENT_RELEASE

Upgrade Jail's etc
------------------

For each jail, run mergemaster.

::

    mergemaster -U -D /path/to/jail

The ``-i`` option cannot be used because of the symlinks used for some directories such as ``/boot``.
The first time running this on a jail could take a while because no database exists on which files have been modified.

Notes On Merging Files
~~~~~~~~~~~~~~~~~~~~~~

* Delete anything that tries to install new files in ``/boot``.
  The jails already have a symlink for ``/boot`` into the basejail so they will get the right files when running.
* Install files that are missing.
  The majority of missing files are new for the release.
  Using the ``-i`` option would automatically install them but it can't be used because of some symlinks.
* Delete files that are managed by Ansible.
  If you see anything that starts with ``# Managed by Ansible`` then don't bother trying to merge the changes now.
  Any changes should be handled by a pull-request to the Ansible repository.


Upgrade Jail's Packages
-----------------------
This can use ``pkg`` if you ``jexec`` to the jail.
I use this script to upgrade all of the jails.

::

    for jid in $(jls | grep -v JID | awk '{print $1}'); do
        jail_hostname=$(jls -j $jid | grep -v JID | awk '{print $3}')
        echo "===== $jid: $jail_hostname"
        sudo jexec $jid pkg update &&
            sudo jexec $jid pkg upgrade pkg &&
            sudo jexec $jid pkg upgrade
    done


From Source
-----------

This part of the document is for historical purposes.
It will be deleted once all hosts and jails use ``freebsd-update``.

Much of this document is based on the Handbook, section 24.6 Rebuilding World.
That should be the primary source to use when upgrading.

::

    # Update /usr/src. It is a git clone of a mirror on github.

    # Start a script session to log everything for review.
    script /var/tmp/mw.out
    chflags -R noschg /usr/obj/*
    rm -rf /usr/obj

    cd /usr/src
    make -j8 buildworld
    make -j8 buildkernel KERNCONF=$kernel
    make installkernel KERNCONF=$kernel
    mergemaster -Fp
    make installworld
    mergemaster -iFU
    yes | make delete-old

    ezjail-admin update -i

    # For each jail directory:
    mergemaster -FU -D /path/to/jail

    reboot

    # Wait for machine to come back.

    # Resume script output from before.
    script -a /var/tmp/mw.out
    cd /usr/src
    make delete-old-libs

    pkg upgrade

    # For each jail directory:
    # CAVEAT: mailman (in the lists jail) MUST be upgraded via ports.
    jexec $jid pkg upgrade
