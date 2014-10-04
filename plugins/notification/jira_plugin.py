from base import BaseNotificationPlugin
from jira.client import JIRA
from business_logic.models import *
from peewee import JOIN_LEFT_OUTER, fn
import re
import pytz
from dateutil.parser import parse


class JiraTaskUpdated(Model):
    task = ForeignKeyField(Task)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        database = db


class JiraIssueTrackingPlugin(BaseNotificationPlugin):
    def __init__(self, server, username, password, ticket_regexps):
        super(JiraIssueTrackingPlugin, self).__init__()
        self.jira = JIRA(server, basic_auth=(username, password))
        self.ticket_regexps = ticket_regexps

    def execute_if_it_has_to(self, company):
        # jira doesn't need to check if it _has_to_
        pending_updates = Task.select().join(Company).switch(Task).join(JiraTaskUpdated, JOIN_LEFT_OUTER).where(
            (Company.id == company.id) & (
                (~(fn.Exists(JiraTaskUpdated.select().where(JiraTaskUpdated.task == Task.id)))) |
                (JiraTaskUpdated.updated_at < Task.updated_at)
            ))

        company_tz = pytz.timezone(company.timezone)

        for task in pending_updates:
            # get the ticket id
            current_best_position = len(task.description)
            current_match = None
            for regexp in self.ticket_regexps:
                match = re.search('\\b(' + regexp + ')\\b', task.description)
                if match is not None and match.start(1) < current_best_position:
                    current_best_position = match.start(1)
                    current_match = match.group(1)

            if current_match is not None:
                issue = None
                try:
                    issue = self.jira.issue(current_match)
                except:
                    pass

                if issue is not None:
                    # found a ticket!
                    description = task.description
                    if current_best_position == 0:
                        description = re.sub('^[^a-zA-Z0-9\\(]*', '', task.description[len(current_match):])

                    worklog_ready = False
                    for worklog in self.jira.worklogs(issue.id):
                        started = parse(worklog.started).astimezone(company_tz).date()
                        if task.date == started and worklog.comment == description:
                            if worklog.timeSpentSeconds != task.time_spent_seconds:
                                worklog.update(timeSpentSeconds=task.time_spent_seconds)
                            worklog_ready = True

                    if not worklog_ready:
                        # get the timezone suffix on the task's date (considering DST)
                        task_date_with_time = datetime.datetime.combine(task.date, datetime.datetime.min.time())
                        suffix = company_tz.localize(task_date_with_time).strftime('%z')

                        # make it 6pm wherever they are
                        dt = parse(task.date.strftime('%Y-%m-%dT18:00:00') + suffix)
                        self.jira.add_worklog(issue.id, timeSpentSeconds=task.time_spent_seconds, started=dt,
                                              comment=description)

                    task_updated = JiraTaskUpdated()
                    task_updated.task = task
                    task_updated.updated_at = datetime.datetime.utcnow()
                    task_updated.save()