from datetime import date

data = {
    'companies': [
        {
            'name': 'Acme',
            'daily_email': 'test@test.com',
            'issue_tracking_plugin': 'jira_plugin.JiraIssueTrackingPlugin',
            'issue_tracking_data': {
                'server': 'http://127.0.0.1:2990/jira',
                'username': 'admin',
                'password': 'admin'
            },
            'time_tracking_plugin': 'test.TimeTrackingTestPlugin',
            'time_tracking_data': {
                'responses': {
                    date(2014, 1, 1): [
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
                            'description': 'DEV-1532 rewriting the commit_to_jira function',
                            'seconds': 450
                        },
                        {
                            'description': 'standup call',
                            'seconds': 300
                        },
                        {
                            'description': 'DEV-932 checking mailchimp\'s api',
                            'seconds': 1200
                        }
                    ],
                    date(2014, 1, 2): [
                        {
                            'description': 'DEV-1234 wrapping it up',
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
