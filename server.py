#!/usr/bin/env python
import urllib2
import hashlib
import json
import time

import bottle

from config import *


def request(path):
    url = APIBASE + path
    req = urllib2.Request(url, headers={
        'Authorization': 'Basic %s' % ('%s:%s' % (USERNAME, PASSWORD)).encode('base64'),
    })

    try:
        resp = urllib2.urlopen(req)
        return json.loads(resp.read())
    except urllib2.HTTPError, e:
        print str(e)
        return json.loads(e.read())
    except Exception, e:
        print str(e)
        return None


def unixtime_to_iso8601(ts):
    return time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(ts))
    
def iso8601_to_unixtime(ts):
    return time.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')

def unixtime_to_vcal(ts):
    return time.strftime('%Y%m%d', ts)

def shorten_line(line, maxwidth):
    lines = []
    while line:
        lines.append(line[:75])
        line = line[75:]
    return '\r\n '.join(lines)

@bottle.get('/calendar/:schedule_name.ics')
def get_schedule(schedule_name):
    schedule_id = SCHEDULES[schedule_name]
    now = time.time()
    since = now - (86400 * 3) # One week ago
    until = now + (86400 * 90) # Three months from now

    resp = request('/schedules/%s/entries?since=%s&until=%s' % (
        schedule_id,
        unixtime_to_iso8601(since),
        unixtime_to_iso8601(until),
    ))

    cal = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//pagercal//PagerDuty Calendar//EN',
    ]

    for entry in resp['entries']:
        eventid = hashlib.new('sha1', json.dumps(entry)).hexdigest()
        start_time = iso8601_to_unixtime(entry['start'])
        end_time = iso8601_to_unixtime(entry['end'])

        cal += [
            'BEGIN:VEVENT',
            'UID:%s@%s.pagercal' % (eventid, schedule_id),
            'DTSTAMP:%s' % (unixtime_to_vcal(start_time)),
            'DTSTART:%s' % (unixtime_to_vcal(start_time)),
            'DTEND:%s' % (unixtime_to_vcal(end_time)),
            'SUMMARY:%s' % entry['user']['name'],
            'CONTACT:%s' % entry['user']['email'],
            'END:VEVENT',
        ]
    cal.append('END:VCALENDAR')

    result = []
    for line in cal:
        if len(line) > 75:
            line = shorten_line(line, 75)
        result.append(line)
    bottle.response.content_type = 'text/calendar'
    return '\r\n'.join(result) + '\r\n'

if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(port=LISTEN_PORT)
