Nginx role
==========

The nginx role requires the following arguments:

``server_name``
    the fqdn of the server.

    This will be used to name the configuration file as well as the server_name
    parameter for nginx server section.

``nginx_template``
    The template to use to generate the configuration file.  Each template has
    own parameters. The following templates are available (and no attempt to
    validate the value is made):

    ``static``
        A template for static web site configuration.  Parameters:

        ``server_root``
            directory where the static content reside

    ``proxy``
        A template for a simple reverse-proxy setup.  Parameters:

        ``upstream_url``
            <host>:<port> of the upstream

Examples
--------

Static::

    - role: nginx
      server_name: test.buildbot.net
      server_root: /

Proxy::

    - role: nginx
      server_name: test.buildbot.net
      upstream: 192.168.1.0:8010
