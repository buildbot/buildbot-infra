set -e

find . -type d | while read dir; do
    ( cd "${dir}" && /usr/local/bin/python2.7 <<'EOF' > index.html~
import os
import re

meetings = {}
filename_re = re.compile('(?P<name>.+)\.(?P<date>[0-9-]+)\.(?P<ordinal>[0-9]+)\.(?P<extension>.*)')
for dirpath, _, filenames in os.walk('.'):
        for filename in filenames:
                m = filename_re.match(filename)
                if not m:
                        continue
                name, date, ordinal, extension = m.group('name', 'date', 'ordinal', 'extension')
                meeting = meetings.setdefault(name, {}).setdefault(date, {}).setdefault(ordinal,
                        {'name': name, 'date': date, 'ordinal': ordinal})
                meeting[extension] = '{}/{}'.format(dirpath[2:], filename)

def a(href, text):
        return '<a href="{}">{}</a>'.format(href, text)

print """\
<!DOCTYPE html>
<html lang="en">
<head><title>Buildbot Meetings</title></head>
<body>
"""


for name in sorted(meetings):
        print '<h2>', name, '</h2>'
        print '<ul>'
        for date in reversed(sorted(meetings[name])):
                for i, ordinal in enumerate(sorted(meetings[name][date])):
                        meeting = meetings[name][date][ordinal]
                        print '<li>{}:'.format(date),
                        if 'html' in meeting:
                                print a(meeting['html'], 'minutes'),
                        if 'txt' in meeting:
                                print '({})'.format(a(meeting['txt'], 'text')),
                        if 'log.html' in meeting:
                                print a(meeting['log.html'], 'log'),
                        if 'log.txt' in meeting:
                                print '({})'.format(a(meeting['log.txt'], 'text')),
                        print "</li>"
                        
        print '</ul>'

print """\
</body>
</html>
"""
EOF
    mv index.html~ index.html
)

done
