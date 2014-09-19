from findertools import comment
import unittest
import inspect
import sys
import peewee
from test_data import data as test_data
from jira.client import JIRA
from abc import ABCMeta
from playhouse.test_utils import test_database
from business_logic.managers import *

test_db = peewee.SqliteDatabase(':memory:')


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
        company_id = CompaniesMgr.create_company(name='Acme',
                                                 daily_email='test@test.com',
                                                 jira_server=test_data['jira']['server'],
                                                 jira_username=test_data['jira']['username'],
                                                 jira_password=test_data['jira']['password'],
                                                 time_tracking_plugin='timedoctor.TimeDoctorPlugin')

        self.assertFalse(company_id is None or company_id <= 0)

        company = CompaniesMgr.get_company(company_id)

        self.assertFalse(company is None)
        self.assertTrue(company.name == 'Acme')
        self.assertTrue(company.daily_email == 'test@test.com')
        self.assertTrue(company.jira_server == test_data['jira']['server'])
        self.assertTrue(company.jira_username == test_data['jira']['username'])
        self.assertTrue(company.jira_password == test_data['jira']['password'])
        self.assertTrue(company.time_tracking_plugin == 'timedoctor.TimeDoctorPlugin')

        company = CompaniesMgr.get_one()
        self.assertFalse(company is None)

    def test_company_creation_failure(self):
        self.assertRaises(CompanyNameMissing, CompaniesMgr.create_company, name=None,
                          daily_email='test@test.com',
                          jira_server=test_data['jira']['server'],
                          jira_username=test_data['jira']['username'],
                          jira_password=test_data['jira']['password'],
                          time_tracking_plugin='timedoctor.TimeDoctorPlugin')

        self.assertRaises(NotificationMethodMissing, CompaniesMgr.create_company,
                          name='Acme',
                          time_tracking_plugin='timedoctor.TimeDoctorPlugin')

        self.assertRaises(JiraParametersMissing, CompaniesMgr.create_company, name='Acme',
                          daily_email='test@test.com',
                          jira_server=test_data['jira']['server'],
                          jira_username=test_data['jira']['username'],
                          time_tracking_plugin='timedoctor.TimeDoctorPlugin')

        self.assertRaises(JiraParametersMissing, CompaniesMgr.create_company, name='Acme',
                          daily_email='test@test.com',
                          jira_server=test_data['jira']['server'],
                          jira_password=test_data['jira']['password'],
                          time_tracking_plugin='timedoctor.TimeDoctorPlugin')

        self.assertRaises(InvalidPlugin, CompaniesMgr.create_company, name='Acme',
                          daily_email='test@test.com',
                          jira_server=test_data['jira']['server'],
                          jira_username=test_data['jira']['username'],
                          jira_password=test_data['jira']['password'],
                          time_tracking_plugin='invalid.plugin')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
