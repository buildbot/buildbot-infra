#!/usr/bin/env python

# Direct Requirements:
#  Twisted
#  PyOpenSSL
#  service_identity

import csv
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
        pattern = '<%s style="padding: 1px 8px; text-align: left;">%s</%s>'
        return pattern % (elt, cell, elt)
    def linkify(r, c):
        if c == link_field:
            url = d[r][link_url_field]
            return '<a href="%s">%s</a>' % (url, d[r][c])
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

    # At a minimum, need to be able to fit the column headers. The final value
    # is for the row names. Putting it at the end to keep subsequent enumerate
    # calls simple.
    col_widths = [len(c) for c in cols] + [0]
    for r in rows:
        col_widths[-1] = max(col_widths[-1], len(str(r)))
        for i, c in enumerate(cols):
            col_widths[i] = max(col_widths[i], len(str(d[r][c])))

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
            tr.append(format_cell(str(value), False))
        table.append('<tr>' + ''.join(tr) + '</tr>')
    return '<table>\n' + '\n'.join(table) + '\n</table>\n'

def get_trac_tickets(start_day, end_day):
    """
    Get the last week's worth of tickets, where week ends through yesterday.
    """
    def format_trac_tickets(what, body):
        tickets = csv.reader(body.splitlines(), delimiter='\t')
        # Trac returns a tab-delimited file with the header. Skip it.
        next(tickets)
        # Returned format is id, summary, type.
        summary = [{'id': t[0], 'summary': t[1], 'type': t[2],
            'url': TRAC_BUILDBOT_TICKET_URL % {'ticket': t[0]}}
            for t in tickets]
        return (what, summary)

    def summarize_trac_tickets(results):
        each_type = {'Opened': 0, 'Closed': 0}
        ticket_summary = {'Enhancements': each_type.copy(),
            'Defects': each_type.copy(), 'Tasks': each_type.copy(),
            'Regressions': each_type.copy(), 'Undecideds': each_type.copy(),
            'Other': each_type.copy(), 'Total': each_type.copy()}
        opened = {}
        closed = {}
        for success, value in results:
            if not success:
                continue
            what, tickets = value
            for t in tickets:
                Type = t['type'].capitalize() + 's'
                if Type in ticket_summary:
                    ticket_summary[Type][what] += 1
                else:
                    ticket_summary['Other'][what] += 1
                ticket_summary['Total'][what] += 1
                if what == 'Opened':
                    opened[len(opened)] = t
                elif what == 'Closed':
                    closed[len(closed)] = t
        # Convert ticket summary to a table to start the weekly summary.
        row_order = ['Enhancements', 'Defects', 'Regressions', 'Tasks',
            'Undecideds', 'Other', 'Total']
        for r in row_order:
            ticket_summary[r]['Type'] = r
        col_order = ['Type', 'Opened', 'Closed']
        ticket_table = tablify_dict(ticket_summary, row_order=row_order,
                col_order=col_order)
        ticket_overview = '\n'.join(['<h2>Ticket Summary</h2>', ticket_table])

        # Also include a list of every new/reopened and closed tickets.
        col_order = ['id', 'type', 'summary']
        # Left-justify every cell except the first column. Return None for the
        # first column to have it skipped.
        opened_table = tablify_dict(opened, show_header=False,
            col_order=col_order, link_field='id', link_url_field='url')
        opened_overview = '\n'.join(['<h2>New/Reopened Tickets</h2>',
            opened_table])
        closed_table = tablify_dict(closed, show_header=False,
            col_order=col_order, link_field='id', link_url_field='url')
        closed_overview = '\n'.join(['<h2>Closed Tickets</h2>', closed_table])

        trac_summary = [ticket_overview, opened_overview, closed_overview]
        return ('trac', '\n\n'.join(trac_summary))

    trac_query_url = ('%(trac_url)s/query?%(status)s&format=tab'
        '&%(time_arg)s=%(start)s..%(end)s'
        '&col=id&col=summary&col=type&col=status&order=id')
    url_options = {
        'trac_url': TRAC_BUILDBOT_URL,
        'start': start_day,
        'end': end_day,
    }

    agent = Agent(reactor)
    fetches = []
    # Need to make two queries: one to get the new/reopened tickets and a
    # second to get the closed tickets.
    url_options['status'] = 'status=new&status=reopened'
    url_options['time_arg'] = 'time'
    new_url = trac_query_url % (url_options)
    d = agent.request('GET', new_url, HTTP_HEADERS)
    d.addCallback(get_body('Opened', format_trac_tickets))
    fetches.append(d)

    url_options['status'] = 'status=closed'
    url_options['time_arg'] = 'changetime'
    closed_url = trac_query_url % (url_options)
    d = agent.request('GET', closed_url, HTTP_HEADERS)
    d.addCallback(get_body('Closed', format_trac_tickets))
    fetches.append(d)

    dl = defer.DeferredList(fetches, fireOnOneErrback=True, consumeErrors=True)
    dl.addCallback(summarize_trac_tickets)
    return dl

def get_github_prs(project, start_day, end_day):
    """
    Get the last week's worth of tickets, where week ends through yesterday.
    """
    def summarize_github_prs(what, body_json):
        # I don't know a good way to parse the time zone. Github returns
        # ISO8601 in UTC.
        gh_time_format = '%Y-%m-%dT%H:%M:%SZ'
        opened_prs = {}
        closed_prs = {}
        body = json.loads(body_json)
        categories = [
            ('Opened', 'open', 'created_at', opened_prs),
            ('Completed', 'closed', 'closed_at', closed_prs),
        ]
        for pr in body:
            for group in categories:
                _, state, when, pr_dict = group
                # Have to check if the when field is not None. The state is
                # 'closed' for merged and unmerged pull requests. The merged
                # tuple is first, so any pull request that is closed and has a
                # merged_at date will be added there before checking the
                # closed_at date.
                if pr['state'] == state and pr[when] is not None:
                    happened = datetime.strptime(pr[when], gh_time_format)
                    # If this pull request was created outside of the summary
                    # period, skip it.
                    if happened.date() < start_day or happened.date() > end_day:
                        continue
                    pr_dict[len(pr_dict)] = pr

        overviews = []
        for group in categories:
            what, _, _, pr_dict = group
            title = '<h2>%s Pull Requests</h2>' % (what,)
            table = tablify_dict(pr_dict, show_header=False,
                row_order=sorted(pr_dict.keys(), lambda a,b: cmp(b, a)),
                col_order=['number', 'title'],
                link_field='number', link_url_field='html_url')
            overviews.append('\n'.join([title, table]))
        return ('github/' + project, '\n\n'.join(overviews))


    gh_api_url = ('%(api_url)s/repos/%(project)s/pulls?state=all')
    url_options = {'api_url': GITHUB_API_URL, 'project': project}
    url = gh_api_url % (url_options)
    agent = Agent(reactor)
    d = agent.request('GET', url, HTTP_HEADERS)
    d.addCallback(get_body('Github', summarize_github_prs))
    return d


def make_html(results):
    body = (
        '<h1>Trac Tickets</h1>\n'
        '%(trac)s\n'
        '\n\n'
        '<h1 style="padding-top: 1em;">Buildbot Pull Requests</h1>\n'
        '%(github/buildbot/buildbot)s' 
        '\n\n'
        '<h1 style="padding-top: 1em;">Buildbot-Infra Pull Requests</h1>\n'
        '%(github/buildbot/buildbot-infra)s')
    body_parts = {}
    for success, value in results:
        if not success:
            continue
        part, msg = value
        body_parts[part] = msg
    return email % dict(body=body % body_parts)

def send_email(html):
    msg = MIMEText(html, 'html')
    msg['Subject'] = "Buildbot Weekly Summary"
    msg['From'] = 'dustin@v.igoro.us'
    msg['To'] = 'buildbot-devel@lists.sourceforge.net'
    s = smtplib.SMTP('localhost')
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

def main():
    end_day = date.today() - timedelta(1)
    start_day = end_day - timedelta(6)

    #dl = defer.DeferredList([get_trac_tickets()])
    dl = defer.DeferredList([
        get_trac_tickets(start_day, end_day),
        get_github_prs('buildbot/buildbot', start_day, end_day),
        get_github_prs('buildbot/buildbot-infra', start_day, end_day),
    ], fireOnOneErrback=True, consumeErrors=True)
    dl.addCallback(make_html)
    dl.addCallback(send_email)
    dl.addErrback(log.err)
    dl.addCallback(lambda _: reactor.stop())
    reactor.run()


if __name__ == '__main__':
    main()
