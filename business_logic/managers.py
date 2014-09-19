from exceptions import *
from models import Company
import importlib
from plugins.time_tracking.base import BaseTimeTrackingPlugin
from plugins.issue_tracking.base import BaseIssueTrackingPlugin


class CompaniesMgr(object):
    @staticmethod
    def create_company(name, daily_email=None, issue_tracking_plugin=None, issue_tracking_data=None,
                       time_tracking_plugin=None, time_tracking_data=None):
        """ Creates a company in the db

        :param name: Company name
        :type name: str
        :param daily_email: Email where the daily email will be sent to
        :type daily_email: str

        :param time_tracking_plugin: Time Tracking plugin
        :type time_tracking_plugin: str
        :return: Company ID
        :rtype: int
        :raises: NotificationMethodMissing, CompanyNameMissing, InvalidTimeTrackingPlugin
        """

        if name is None:
            raise CompanyNameMissing()

        # There should be at least a notification method
        if daily_email is None and issue_tracking_plugin is None:
            raise NotificationMethodMissing()

        # This throws an exception if the plugin doesn't exist
        PluginsManager.get_time_tracking_plugin(time_tracking_plugin, **time_tracking_data)

        if issue_tracking_plugin is not None:
            PluginsManager.get_issue_tracking_plugin(issue_tracking_plugin, **issue_tracking_data)

        company = Company(name=name, daily_email=daily_email, issue_tracking_plugin=issue_tracking_plugin,
                          issue_tracking_data=issue_tracking_data, time_tracking_plugin=time_tracking_plugin,
                          time_tracking_data=time_tracking_data)
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
        except:
            raise InvalidPlugin()

        if not hasattr(module, class_name):
            raise InvalidPlugin()

        return getattr(module, class_name)(**kwargs)

    @staticmethod
    def get_time_tracking_plugin(name, **kwargs):
        """

        :param name: The name (with the module name) of the plugin to use
        :param kwargs: Values to use on the plugin creation
        :return: An instance of the plugin
        :rtype: BaseTimeTrackingPlugin
        """
        PluginsManager.get_object(name, 'time_tracking', **kwargs)

    @staticmethod
    def get_issue_tracking_plugin(name, **kwargs):
        """

        :param name: The name (with the module name) of the plugin to use
        :param kwargs: Values to use on the plugin creation
        :return: An instance of the plugin
        :rtype: BaseIssueTrackingPlugin
        """
        PluginsManager.get_object(name, 'issue_tracking', **kwargs)