LISTEN_PORT = 9993
APIBASE = 'https://mycompany.pagerduty.com/api/v1'
USERNAME = 'me@mycompany.com'
PASSWORD = 'superseekrit'

# You need to get the schedule ID by looking at the URL
# of the schedule page on the PagerDuty website. It should
# be something like
# http://mycompany.pagerduty.com/schedule/rotations/P000000
SCHEDULES = {
    'operations': 'P000000',
}
