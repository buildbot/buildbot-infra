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

    ``domain-redirect``
        A template for redirecting traffic for the whole domain to another one.
        Parameters:

        ``server_names``
            list of server names that should be redirected to another domain

        ``target_url``
            URL of the target server including scheme (e.g. http://buildbot.net)

        .. note::

           For this template, ``server_names`` gives the hostnames that nginx will redirect; the common ``server_name`` parameter is only used to name the configuration file.

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

Domain Redirect::

    - role: nginx
      server_name: redirects
      server_names:
      - www.buildbot.net
      - www.buildbot.org
      - buildbot.org
      target_url: http://buildbot.net
