from exceptions import *
from models import Company


class CompaniesMgr:
    @staticmethod
    def create_company(name, daily_email=None, jira_domain=None, jira_username=None, jira_password=None):
        """ Creates a company in the db

        :param name: Company name
        :type name: str
        :param daily_email: Email where the daily email will be sent to
        :type daily_email: str
        :param jira_domain: JIRA Domain
        :type jira_domain: str
        :param jira_username: JIRA Username
        :type jira_username: str
        :param jira_password: JIRA Password
        :type jira_password: str
        :return: Company ID
        :rtype: int
        :raises: NotificationMethodMissing, JiraParametersMissing, CompanyNameMissing
        """

        if name is None:
            raise CompanyNameMissing()

        # There should be at least a notification method
        if daily_email is None and jira_domain is None:
            raise NotificationMethodMissing()

        # If there's domain, check that we have user and pass
        if jira_domain is not None and (jira_username is None or jira_password is None):
            raise JiraParametersMissing()

        company = Company(name=name, daily_email=daily_email, jira_domain=jira_domain, jira_username=jira_username,
                          jira_password=jira_password)
        company.save()

        return company.id

    @staticmethod
    def get_company(company_id):
        """ Gets a company with the given id

        :param company_id: The ID of the company
        :type company_id: int
        :return: The company if exists
        :rtype: Company
        :raises: CompanyNotFound
        """
        res = Company.get(Company.id == company_id)

        if res is None:
            raise CompanyNotFound

        return res
