from base import BaseIssueTrackingPlugin
from jira.client import JIRA


class JiraIssueTrackingPlugin(BaseIssueTrackingPlugin):
    def __init__(self, server, username, password):
        super(JiraIssueTrackingPlugin, self).__init__()
        self.jira = JIRA(server, basic_auth=(username, password))
