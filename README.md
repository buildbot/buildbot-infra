# Ansible:

Run `ansible-playbook -i prod-hosts -s site.yml` to configure the production site.

## Development

During development, you may create a `dev-hosts` file containing your test hosts.
Then run `ansible-playbook -s site.yml` to test your changes.

# Other files:

 * buildbot.asc - Buildbot Release Team Keyring
 * scripts/ - some scripts not under configuration management yet
