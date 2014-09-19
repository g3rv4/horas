from exceptions import *
from models import Company
import importlib
import sys
from plugins.time_tracking.base import BaseTimeTrackingPlugin


class CompaniesMgr(object):
    @staticmethod
    def create_company(name, daily_email=None, jira_server=None, jira_username=None, jira_password=None,
                       time_tracking_plugin=None):
        """ Creates a company in the db

        :param name: Company name
        :type name: str
        :param daily_email: Email where the daily email will be sent to
        :type daily_email: str
        :param jira_server: JIRA Server URL
        :type jira_server: str
        :param jira_username: JIRA Username
        :type jira_username: str
        :param jira_password: JIRA Password
        :type jira_password: str
        :param time_tracking_plugin: Time Tracking plugin
        :type time_tracking_plugin: str
        :return: Company ID
        :rtype: int
        :raises: NotificationMethodMissing, JiraParametersMissing, CompanyNameMissing, InvalidTimeTrackingPlugin
        """

        if name is None:
            raise CompanyNameMissing()

        # There should be at least a notification method
        if daily_email is None and jira_server is None:
            raise NotificationMethodMissing()

        # This throws an exception if the plugin doesn't exist
        PluginsManager.get_time_tracking_plugin(time_tracking_plugin)

        # If there's domain, check that we have user and pass
        if jira_server is not None and (jira_username is None or jira_password is None):
            raise JiraParametersMissing()

        company = Company(name=name, daily_email=daily_email, jira_server=jira_server, jira_username=jira_username,
                          jira_password=jira_password, time_tracking_plugin=time_tracking_plugin)
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

    @staticmethod
    def get_one():
        return Company.get(Company.id > 0)


class PluginsManager(object):
    @staticmethod
    def get_object(name, package, **kwargs):
        # separate get the module and the class
        parts = name.split('.')
        module = ".".join(parts[:-1])
        class_name = parts[-1]
        full_module_name = 'plugins.' + package + '.' + module

        try:
            # import the module
            module = importlib.import_module(full_module_name)
            if not hasattr(module, class_name):
                raise InvalidPlugin()

            return getattr(module, class_name)(**kwargs)
        except:
            raise InvalidPlugin()

    @staticmethod
    def get_time_tracking_plugin(name, **kwargs):
        """

        :param name: The name (with the module name) of the plugin to use
        :return: An instance of the plugin
        :rtype: BaseTimeTrackingPlugin
        """
        PluginsManager.get_object(name, 'time_tracking', **kwargs)
