import requests
import smtplib

FROM = 'dustin@buildbot.net'
RECIPIENT = 'devel@buildbot.net'


def main():
    r = requests.get(
        'https://api.github.com/repos/buildbot/buildbot/issues?labels=merge me'
    )
    body = ["%(html_url)s - %(title)s" % pr for pr in r.json()]
    if not body:
        return

    body = "Mergeable pull requests:\n\n" + "\n".join(body)

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(FROM, RECIPIENT, """\
Subject: Mergeable Buildbot pull requests
From: %s
To: %s

%s""" % (FROM, RECIPIENT, body))


if __name__ == "__main__":
    main()
