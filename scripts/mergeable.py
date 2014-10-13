#! /usr/bin/env python

import sys
import requests
import getpass
import smtplib

def main():
    r = requests.get('https://api.github.com/repos/buildbot/buildbot/issues?labels=merge-me')
    body = [ "%(html_url)s - %(title)s" % pr for pr in r.json() ]
    if not body:
        return

    body = "Mergeable pull requests:\n\n" + "\n".join(body)

    address = sys.argv[1]
    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(getpass.getuser(), [address], """\
Subject: Mergeable Buildbot pull requests
To: %s

%s""" % (address, body))

if __name__ == "__main__":
    main()
