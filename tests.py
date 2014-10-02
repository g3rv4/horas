import unittest
import inspect
import peewee
import sys
import copy
import itertools
from test_data import data as test_data
from abc import ABCMeta
from playhouse.test_utils import test_database
from business_logic.managers import *
from business_logic.models import *

test_db = peewee.SqliteDatabase('test.db')


class TestCaseWithPeewee(unittest.TestCase):
    """
    This abstract class is used to "inject" the test database so that the tests don't use the real sqlite db
    """

    __metaclass__ = ABCMeta

    def run(self, result=None):
        model_classes = [m[1] for m in inspect.getmembers(sys.modules['business_logic.models'], inspect.isclass) if
                         issubclass(m[1], peewee.Model) and m[1] != peewee.Model]
        with test_database(test_db, model_classes):
            super(TestCaseWithPeewee, self).run(result)


class TestCompanyCreation(TestCaseWithPeewee):
    def test_company_creation(self):
        for company_data in test_data['companies']:
            company_id = CompaniesMgr.create_company(name=company_data['name'],
                                                     notification_plugins=company_data['notification_plugins'],
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
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(NotificationMethodMissing, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=None,
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

        company_data_copied = copy.deepcopy(company_data)
        company_data_copied['notification_plugins'][0]['notification_plugin'] = 'InvalidPlugin'
        self.assertRaises(InvalidPlugin, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=company_data_copied['notification_plugins'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(InvalidPlugin, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=company_data['notification_plugins'],
                          time_tracking_plugin='invalid.Plugin',
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(Exception, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=company_data['notification_plugins'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=None)

        company_data_copied = copy.deepcopy(company_data)
        company_data_copied['notification_plugins'][0]['notification_data'] = None
        self.assertRaises(Exception, CompaniesMgr.create_company, name=company_data['name'],
                          notification_plugins=company_data_copied['notification_plugins'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])


class TestTimeTrackingData(TestCaseWithPeewee):
    def setUp(self):
        self.company_data = \
            [c for c in test_data['companies'] if c['time_tracking_plugin'] == 'test.TimeTrackingTestPlugin'][0]

        self.company_id = CompaniesMgr.create_company(name=self.company_data['name'],
                                                      notification_plugins=self.company_data['notification_plugins'],
                                                      time_tracking_plugin=self.company_data['time_tracking_plugin'],
                                                      time_tracking_data=self.company_data['time_tracking_data'])

    def test_time_tracking_storage(self):
        for date in self.company_data['time_tracking_data']['responses']:
            time_tracking_results = self.company_data['time_tracking_data']['responses'][date]
            # element to group by
            grouping_fn = lambda x: x['description']

            # sort the elements (groupby needs them sorted)
            elements = sorted(time_tracking_results, key=grouping_fn)
            groups = itertools.groupby(elements, grouping_fn)
            res = dict([(r[0], sum([item['seconds'] for item in r[1]])) for r in groups])

            CompaniesMgr.update_tasks(self.company_id, date, time_tracking_results)

            # Call it twice to see how it handles updates
            CompaniesMgr.update_tasks(self.company_id, date, time_tracking_results)

            company = CompaniesMgr.get_company(self.company_id)

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
                                                      time_tracking_plugin=self.company_data['time_tracking_plugin'],
                                                      time_tracking_data=self.company_data['time_tracking_data'])

        for date in self.company_data['time_tracking_data']['responses']:
            time_tracking_results = self.company_data['time_tracking_data']['responses'][date]
            CompaniesMgr.update_tasks(self.company_id, date, time_tracking_results)

    def test_jira_issue_tracking(self):
        pass


def main():
    unittest.main()


if __name__ == '__main__':
    main()
