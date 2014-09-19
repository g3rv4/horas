import unittest
import inspect
import peewee
import sys
from test_data import data as test_data
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
        for company_data in test_data['companies']:
            company_id = CompaniesMgr.create_company(name=company_data['name'],
                                                     daily_email=company_data['daily_email'],
                                                     issue_tracking_plugin=company_data['issue_tracking_plugin'],
                                                     issue_tracking_data=company_data['issue_tracking_data'],
                                                     time_tracking_plugin=company_data['time_tracking_plugin'],
                                                     time_tracking_data=company_data['time_tracking_data'])

            self.assertFalse(company_id is None or company_id <= 0)

            company = CompaniesMgr.get_company(company_id)

            self.assertFalse(company is None)
            self.assertTrue(company.name == company_data['name'])
            self.assertTrue(company.issue_tracking_plugin == company_data['issue_tracking_plugin'])
            self.assertTrue(company.issue_tracking_data == company_data['issue_tracking_data'])
            self.assertTrue(company.time_tracking_plugin == company_data['time_tracking_plugin'])
            self.assertTrue(company.time_tracking_data == company_data['time_tracking_data'])

            company = CompaniesMgr.get_one()
            self.assertFalse(company is None)

    def test_company_creation_failure(self):
        company_data = test_data['companies'][0]
        self.assertRaises(CompanyNameMissing, CompaniesMgr.create_company, name=None,
                          daily_email=company_data['daily_email'],
                          issue_tracking_plugin=company_data['issue_tracking_plugin'],
                          issue_tracking_data=company_data['issue_tracking_data'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(NotificationMethodMissing, CompaniesMgr.create_company, name=company_data['name'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(InvalidPlugin, CompaniesMgr.create_company, name=company_data['name'],
                          daily_email=company_data['daily_email'],
                          issue_tracking_plugin='invalid.Plugin',
                          issue_tracking_data=company_data['issue_tracking_data'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(InvalidPlugin, CompaniesMgr.create_company, name=company_data['name'],
                          daily_email=company_data['daily_email'],
                          issue_tracking_plugin=company_data['issue_tracking_plugin'],
                          issue_tracking_data=company_data['issue_tracking_data'],
                          time_tracking_plugin='invalid.Plugin',
                          time_tracking_data=company_data['time_tracking_data'])

        self.assertRaises(Exception, CompaniesMgr.create_company, name=company_data['name'],
                          daily_email=company_data['daily_email'],
                          issue_tracking_plugin=company_data['issue_tracking_plugin'],
                          issue_tracking_data=company_data['issue_tracking_data'],
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=None)

        self.assertRaises(Exception, CompaniesMgr.create_company, name=company_data['name'],
                          daily_email=company_data['daily_email'],
                          issue_tracking_plugin=company_data['issue_tracking_plugin'],
                          issue_tracking_data=None,
                          time_tracking_plugin=company_data['time_tracking_plugin'],
                          time_tracking_data=company_data['time_tracking_data'])

def main():
    unittest.main()


if __name__ == '__main__':
    main()
