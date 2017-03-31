#!/usr/bin/env python

# Direct Requirements:
#  Twisted
#  PyOpenSSL
#  service_identity

import json
import textwrap
import smtplib

from email.mime.text import MIMEText
from datetime import date
from datetime import datetime
from datetime import timedelta
from functools import partial
from twisted.python import log
from twisted.internet import defer
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.client import readBody
from twisted.web.http_headers import Headers

TRAC_BUILDBOT_URL = 'http://trac.buildbot.net'
TRAC_BUILDBOT_TICKET_URL = TRAC_BUILDBOT_URL + '/ticket/%(ticket)s'
GITHUB_API_URL = 'https://api.github.com'
HTTP_HEADERS = Headers({'User-Agent': ['buildbot.net weekly summary']})
FROM = 'dustin@buildbot.net'
RECIPIENTS = ['devel@buildbot.net', 'users@buildbot.net']

WEEKLY_MEETING_TEXT = textwrap.dedent("""

    <p>Buildbot has weekly meetings via irc, held at 17:00 UTC on Tuesdays.
    That is about 2 hours from now!

    <p>Meetings are in #buildbot on Freenode, open to any and all participants.
    They generally focus on organizational, rather than technical issues,
    but are open to anything Buildbot-related.
    To raise a topic, add it to "All Other Business" in the
    <a href="https://titanpad.com/buildbot-agenda">agenda</a>,
    or just speak up during the meeting.

    <p>Meeting minutes are available
    <a href="https://supybot.buildbot.net/meetings/">here</a>.
    """)

email = textwrap.dedent("""\
    <html>
    <head>
    </head>
    <body>
    %(body)s
    </body>
    </html>
    """)


def get_body(what, f):
    def cb(resp):
        d = readBody(resp)
        d.addCallback(partial(f, what))
        return d
    return cb


def tablify_dict(d, show_header=True, row_order=None, col_order=None,
                 link_field=None, link_url_field=None):
    def format_cell(cell, is_header):
        elt = 'th' if is_header else 'td'
        pattern = u'<%s style="padding: 1px 8px; text-align: left;">%s</%s>'
        return pattern % (elt, cell, elt)

    def linkify(r, c):
        if c == link_field:
            url = d[r][link_url_field]
            return u'<a href="%s">%s</a>' % (url, d[r][c])
        return d[r][c]

    if row_order is None:
        rows = sorted(d.keys())
    else:
        rows = row_order

    # All values of the dict should have the same keys.
    if col_order is None:
        cols = sorted(d[rows[0]].keys())
    else:
        cols = col_order

    # convert everything to unicode, and don't look back
    for r in rows:
        for c in cols:
            if not isinstance(d[r][c], unicode):
                d[r][c] = unicode(d[r][c])

    # At a minimum, need to be able to fit the column headers. The final value
    # is for the row names. Putting it at the end to keep subsequent enumerate
    # calls simple.
    col_widths = [len(c) for c in cols] + [0]
    for r in rows:
        col_widths[-1] = max(col_widths[-1], len(unicode(r)))
        for i, c in enumerate(cols):
            col_widths[i] = max(col_widths[i], len(d[r][c]))

    # The first row of the table is the header.
    if show_header:
        th_row = [format_cell(c, True) for c in cols]
        th = ''.join(th_row)
        table = ['<tr>' + th + '</tr>']
    else:
        table = []
    for r in rows:
        tr = []
        for i, c in enumerate(cols):
            value = linkify(r, c)
            tr.append(format_cell(value, False))
        table.append('<tr>' + ''.join(tr) + '</tr>')
    return '<table>\n' + '\n'.join(table) + '\n</table>\n'


def get_github_issues(project, start_day, end_day, issue_type='pulls'):
    """
    Get the last week's worth of tickets, where week ends through yesterday.
    """
    def summarize_github_issues(what, body_json):
        # I don't know a good way to parse the time zone. Github returns
        # ISO8601 in UTC.
        gh_time_format = '%Y-%m-%dT%H:%M:%SZ'
        opened_issues = {}
        closed_issues = {}
        body = json.loads(body_json)
        categories = [
            ('Opened', 'open', 'created_at', opened_issues),
            ('Completed', 'closed', 'closed_at', closed_issues),
        ]
        for iss in body:
            # skip pull requests, which GH returns in lists of issues
            if issue_type == 'issues' and 'pull_request' in iss:
                continue
            for group in categories:
                _, state, when, pr_dict = group
                # Have to check if the when field is not None. The state is
                # 'closed' for merged and unmerged pull requests. The merged
                # tuple is first, so any pull request that is closed and has a
                # merged_at date will be added there before checking the
                # closed_at date.
                if iss['state'] == state and iss[when] is not None:
                    happened = datetime.strptime(iss[when], gh_time_format)
                    # If this pull request was created outside of the summary
                    # period, skip it.
                    if not (start_day <= happened.date() <= end_day):
                        continue
                    pr_dict[len(pr_dict)] = iss

        overviews = []
        for group in categories:
            what, _, _, pr_dict = group
            if not pr_dict:
                continue
            typename = {'issues': 'Issues', 'pulls': 'Pull Requests'}[issue_type]
            title = '<h2>%s %s</h2>' % (what, typename)
            table = tablify_dict(
                pr_dict, show_header=False,
                row_order=sorted(pr_dict.keys(), lambda a, b: cmp(b, a)),
                col_order=['number', 'title'],
                link_field='number', link_url_field='html_url')
            overviews.append('\n'.join([title, table]))
        identifier = 'github/{}/{}'.format(project, issue_type)
        if overviews:
            return (identifier, '\n'.join(overviews))
        else:
            return (identifier, '<i>None this week</i>')

    gh_api_url = ('%(api_url)s/repos/%(project)s/%(issue_type)s?state=all')
    url_options = {'api_url': GITHUB_API_URL, 'project': project, 'issue_type': issue_type}
    url = gh_api_url % (url_options)
    agent = Agent(reactor)
    d = agent.request('GET', url, HTTP_HEADERS)
    d.addCallback(get_body('Github', summarize_github_issues))
    return d


def make_html(results):
    body = (
        '<h1>Weekly Meeting</h1>\n'
        '%(weekly-meeting)s\n'
        '<h1 style="padding-top: 1em;">Buildbot Issues</h1>\n'
        '%(github/buildbot/buildbot/issues)s\n'
        '<h1 style="padding-top: 1em;">Buildbot Pull Requests</h1>\n'
        '%(github/buildbot/buildbot/pulls)s\n'
        '<h1 style="padding-top: 1em;">Buildbot-Infra Pull Requests</h1>\n'
        '%(github/buildbot/buildbot-infra/pulls)s\n'
        '<h1 style="padding-top: 1em;">Meta-buildbot Pull Requests</h1>\n'
        '%(github/buildbot/metabbotcfg/pulls)s\n'
    )
    body_parts = {}
    for success, value in results:
        if not success:
            continue
        part, msg = value
        body_parts[part] = msg
    body_parts['weekly-meeting'] = WEEKLY_MEETING_TEXT
    return email % dict(body=body % body_parts)


def send_email(html):
    msg = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    msg['Subject'] = "Buildbot Weekly Summary"
    msg['From'] = FROM
    msg['To'] = ', '.join(RECIPIENTS)
    s = smtplib.SMTP('localhost')
    s.sendmail(msg['From'], RECIPIENTS, msg.as_string())
    s.quit()


def main():
    end_day = date.today()
    start_day = end_day - timedelta(7)

    dl = defer.DeferredList([
        get_github_issues('buildbot/buildbot', start_day, end_day, 'issues'),
        get_github_issues('buildbot/buildbot', start_day, end_day, 'pulls'),
        get_github_issues('buildbot/buildbot-infra', start_day, end_day),
        get_github_issues('buildbot/metabbotcfg', start_day, end_day),
    ], fireOnOneErrback=True, consumeErrors=True)
    dl.addCallback(make_html)
    dl.addCallback(send_email)
    dl.addErrback(log.err)
    dl.addCallback(lambda _: reactor.stop())
    reactor.run()


if __name__ == '__main__':
    main()
