from datetime import datetime

data = {
    'companies': [
        {
            'name': 'Acme',
            'timezone': 'US/Pacific',  # Use a pytz timezone name
            'notification_plugins': [
                {
                    'notification_plugin': 'jira_plugin.JiraIssueTrackingPlugin',
                    'notification_data': {
                        'server': 'http://127.0.0.1:2990/jira',
                        'username': 'admin',
                        'password': 'admin',
                        'ticket_regexps': [
                            'TEST-[0-9]+',
                            'DEV-[0-9]+'
                        ]
                    },
                }
            ],
            'time_tracking_plugin': 'test.TimeTrackingTestPlugin',
            'time_tracking_data': {
                'responses': {
                    datetime(2014, 1, 1, 10, 0, 0): [
                        {
                            'description': 'standup call',
                            'seconds': 2130
                        },
                        {
                            'description': 'DEV-1234 trying to understand the bug',
                            'seconds': 600
                        },
                        {
                            'description': 'DEV-1234 going through the db schema',
                            'seconds': 300
                        },
                        {
                            'description': 'rewriting the commit_to_jira function (as defined at DEV-1532), also affects DEV-1534',
                            'seconds': 450
                        },
                        {
                            'description': 'standup call',
                            'seconds': 300
                        },
                        {
                            'description': 'TEST-1 checking mailchimp\'s api',
                            'seconds': 1200
                        }
                    ],
                    datetime(2014, 1, 1, 17, 0, 0): [
                        {
                            'description': 'standup call',
                            'seconds': 2130
                        },
                        {
                            'description': 'DEV-1234 trying to understand the bug',
                            'seconds': 600
                        },
                        {
                            'description': 'DEV-1234 going through the db schema',
                            'seconds': 300
                        },
                        {
                            'description': 'rewriting the commit_to_jira function (as defined at DEV-1532), also affects DEV-1534',
                            'seconds': 450
                        },
                        {
                            'description': 'standup call',
                            'seconds': 300
                        },
                        {
                            'description': 'TEST-1 checking mailchimp\'s api',
                            'seconds': 1200
                        },
                        {
                            'description': 'TEST-1 checking mailchimp\'s api',
                            'seconds': 600
                        }
                    ],
                    datetime(2014, 1, 2, 10, 30, 0): [
                        {
                            'description': 'TEST-1 wrapping it up',
                            'seconds': 4200
                        },
                        {
                            'description': 'mailchimp integration demo',
                            'seconds': 3060
                        }
                    ]
                }
            }
        }
    ]
}
