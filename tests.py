import unittest
import inspect
import peewee
import sys
import copy
import itertools
import re
from test_data import data as test_data
from abc import ABCMeta
from jira.client import JIRA
from playhouse.test_utils import test_database
from business_logic.managers import *
from business_logic.models import *
from dateutil.parser import parse
import pytz

# need to import all the plugins that have DB tables so that TestCaseWithPeewee's run() method loads them
import plugins.notification.jira_plugin
#########################################################################################################

test_db = peewee.SqliteDatabase('test'+datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+'.db')


class TestCaseWithPeewee(unittest.TestCase):
    """
    This abstract class is used to "inject" the test database so that the tests don't use the real sqlite db
    """

    __metaclass__ = ABCMeta

    def run(self, result=None):
        model_classes = []
        for module in [m for m in sys.modules if m.startswith('plugins') or m.startswith('business_logic')]:
            model_classes += [m[1] for m in inspect.getmembers(sys.modules[module], inspect.isclass) if
                         issubclass(m[1], peewee.Model) and m[1] != peewee.Model and m[1] not in model_classes]
        with test_database(test_db, model_classes):
            super(TestCaseWithPeewee, self).run(result)


class TestCompanyCreation(TestCaseWithPeewee):
    def test_company_creation(self):
        for company_data in test_data['companies']:
            company_id = CompaniesMgr.create_company(name=company_data['name'],
                                                     notification_plugins=company_data['notification_plugins'],
                                                     timezone=company_data['timezone'],
                                                     time_tracking_plugin=company_data['time_tracking_plugin'],
                                                     time_tracking_data=company_data['time_tracking_data'])

            self.assertFalse(company_id is None or company_id <= 0)

            company = CompaniesMgr.get_company(company_id)

            self.assertFalse(company is None)
            self.assertTrue(company.name == company_data['name'])
            self.assertTrue(company.notification_plugins == company_data['notification_plugins'])
            self.assertTrue(company.time_tracking_plugin == company_data['time_tracking_plugin'])
            self.assertTrue(company.time_tracking_data == company_data['time_tracking_data'])

    def test_company_creation_failure(self):
        company_data = test_data['companies'][0]
        self.assertRaises(CompanyNameMissing, CompaniesMgr.create_company, name=None,
                          notification_plugins=company_data['notification_plugins'],
                          timezone=company_data['timezone'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(TimezoneMissing, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=company_data['notification_plugins'],
                          timezone=None,
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(NotificationMethodMissing, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=None,
                          timezone=company_data['timezone'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

        company_data_copied = copy.deepcopy(company_data)
        company_data_copied['notification_plugins'][0]['notification_plugin'] = 'InvalidPlugin'
        self.assertRaises(InvalidPlugin, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=company_data_copied['notification_plugins'],
                          timezone=company_data['timezone'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(InvalidPlugin, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=company_data['notification_plugins'],
                          timezone=company_data['timezone'],
                          time_tracking_plugin='invalid.Plugin',
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(Exception, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=company_data['notification_plugins'],
                          timezone=company_data['timezone'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=None)

        company_data_copied = copy.deepcopy(company_data)
        company_data_copied['notification_plugins'][0]['notification_data'] = None
        self.assertRaises(Exception, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=company_data_copied['notification_plugins'],
                          timezone=company_data['timezone'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])


class TestTimeTrackingData(TestCaseWithPeewee):
    def setUp(self):
        self.company_data = \
            [c for c in test_data['companies'] if c['time_tracking_plugin'] == 'test.TimeTrackingTestPlugin'][0]

        self.company_id = CompaniesMgr.create_company(name=self.company_data['name'],
                                                      notification_plugins=self.company_data['notification_plugins'],
                                                      timezone=self.company_data['timezone'],
                                                      time_tracking_plugin=self.company_data['time_tracking_plugin'],
                                                      time_tracking_data=self.company_data['time_tracking_data'])

    def test_time_tracking_storage(self):
        for datet in self.company_data['time_tracking_data']['responses']:
            date = datet.date()
            time_tracking_results = self.company_data['time_tracking_data']['responses'][datet]

            CompaniesMgr.update_tasks(self.company_id, date, time_tracking_results)

            # Call it twice to see how it handles updates
            CompaniesMgr.update_tasks(self.company_id, date, time_tracking_results)

            company = CompaniesMgr.get_company(self.company_id)

            res = get_aggregated_time_tracking_results(time_tracking_results)

            # check that all the tasks are created
            for task in company.tasks.where(Task.date == date):
                self.assertTrue(task.description in res)
                self.assertTrue(task.time_spent_seconds == res[task.description])
                del (res[task.description])

            # check that there's no one missing
            self.assertTrue(len(res) == 0)


class TestJiraIssueTracking(TestCaseWithPeewee):
    def setUp(self):
        self.company_data = \
            [c for c in test_data['companies'] if c['time_tracking_plugin'] == 'test.TimeTrackingTestPlugin' and any(
                item['notification_plugin'] == 'jira_plugin.JiraIssueTrackingPlugin' for item in
                c['notification_plugins'])][0]

        self.company_id = CompaniesMgr.create_company(name=self.company_data['name'],
                                                      notification_plugins=self.company_data['notification_plugins'],
                                                      timezone=self.company_data['timezone'],
                                                      time_tracking_plugin=self.company_data['time_tracking_plugin'],
                                                      time_tracking_data=self.company_data['time_tracking_data'])

        company_tz = pytz.timezone(self.company_data['timezone'])

        for datet in self.company_data['time_tracking_data']['responses']:
            date = datet.date()
            time_tracking_results = self.company_data['time_tracking_data']['responses'][datet]
            CompaniesMgr.update_tasks(self.company_id, date, time_tracking_results)
            CompaniesMgr.trigger_notifications(self.company_id)

            # verify that the referenced tickets have the updated values
            res = get_aggregated_time_tracking_results(time_tracking_results)

            jira_plugin_conf = [conf['notification_data'] for conf in self.company_data['notification_plugins'] if
                                conf['notification_plugin'] == 'jira_plugin.JiraIssueTrackingPlugin'][0]

            jira = JIRA(jira_plugin_conf['server'],
                        basic_auth=(jira_plugin_conf['username'], jira_plugin_conf['password']))

            for key in res:
                current_best_position = len(key)
                current_match = None
                for regexp in jira_plugin_conf['ticket_regexps']:
                    match = re.search('\\b(' + regexp + ')\\b', key)
                    if match is not None and match.start(1) < current_best_position:
                        current_best_position = match.start(1)
                        current_match = match.group(1)

                if current_match is not None:
                    # found a ticket!
                    description = key
                    success = False
                    if current_best_position == 0:
                        description = re.sub('^[^a-zA-Z0-9\\(]*', '', key[len(current_match):])

                    issue = None
                    try:
                        issue = jira.issue(current_match)
                    except:
                        # if there's no ticket created, just skip it
                        success = True

                    if issue:
                        for worklog in jira.worklogs(issue.id):
                            created = parse(worklog.started).astimezone(company_tz).date()
                            if date == created and worklog.comment == description and worklog.timeSpentSeconds == res[
                                key]:
                                success = True

                    self.assertTrue(success)

                    print(key + ': ' + current_match)


    def test_jira_issue_tracking(self):
        pass


def get_aggregated_time_tracking_results(results):
    # element to group by
    grouping_fn = lambda x: x['description']

    # sort the elements (groupby needs them sorted)
    elements = sorted(results, key=grouping_fn)
    groups = itertools.groupby(elements, grouping_fn)
    return dict([(r[0], sum([item['seconds'] for item in r[1]])) for r in groups])


def main():
    unittest.main()


if __name__ == '__main__':
    main()
