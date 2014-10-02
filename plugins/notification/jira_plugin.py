from base import BaseNotificationPlugin
from jira.client import JIRA


class JiraIssueTrackingPlugin(BaseNotificationPlugin):
    def __init__(self, server, username, password, ticket_regexps):
        super(JiraIssueTrackingPlugin, self).__init__()
        self.jira = JIRA(server, basic_auth=(username, password))
        self.ticket_regexps = ticket_regexps
