import unittest
import inspect
import sys
import peewee
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
        company_id = CompaniesMgr.create_company('Acme', 'test@test.com', 'acme.atlassian.net', 'username', 'pass')

        self.failIf(company_id is None or company_id <= 0)

        company = CompaniesMgr.get_company(company_id)

        self.failIf(company is None)
        self.failUnless(company.name == 'Acme')
        self.failUnless(company.daily_email == 'test@test.com')
        self.failUnless(company.jira_domain == 'acme.atlassian.net')
        self.failUnless(company.jira_username == 'username')
        self.failUnless(company.jira_password == 'pass')

    def test_company_creation_failure(self):
        self.assertRaises(CompanyNameMissing, CompaniesMgr.create_company, name=None)
        self.assertRaises(NotificationMethodMissing, CompaniesMgr.create_company, name='Acme')
        self.assertRaises(JiraParametersMissing, CompaniesMgr.create_company, name='Acme',
                          jira_domain='acme.atlassian.net')




def main():
    unittest.main()


if __name__ == '__main__':
    main()
