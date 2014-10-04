from exceptions import *
from models import Company, Task
import importlib
import itertools
from plugins.time_tracking.common import BaseTimeTrackingPlugin
from plugins.notification.base import BaseNotificationPlugin


class CompaniesMgr(object):
    @staticmethod
    def create_company(name, notification_plugins, timezone, time_tracking_plugin=None, time_tracking_data=None):
        """ Creates a company in the db

        :param name: Company name
        :type name: str
        :param notification_plugins: List of plugins to use to notify
        :type notification_plugins: [BaseNotificationPlugin]
        :param timezone: Timezone the company is in (as pytz requires it)
        :type timezone: str
        :param time_tracking_plugin: Time Tracking plugin
        :type time_tracking_plugin: str
        :return: Company ID
        :rtype: int
        :raises: NotificationMethodMissing, CompanyNameMissing, InvalidTimeTrackingPlugin
        """

        if name is None:
            raise CompanyNameMissing()

        if timezone is None:
            raise TimezoneMissing()

        # There should be at least a notification method
        if notification_plugins is None or len(notification_plugins) == 0:
            raise NotificationMethodMissing()

        # This throws an exception if the plugin doesn't exist
        PluginsManager.get_time_tracking_plugin(time_tracking_plugin, **time_tracking_data)

        for plugin in notification_plugins:
            PluginsManager.get_notification_plugin(plugin['notification_plugin'], **plugin['notification_data'])

        company = Company(name=name, notification_plugins=notification_plugins, timezone=timezone,
                          time_tracking_plugin=time_tracking_plugin, time_tracking_data=time_tracking_data)
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
    def update_tasks(company_id, date, time_tracking_results):
        """ Updates the data from the time tracking plugin into the database

        :param company_id: The ID of the company
        :type company_id: int
        :param date: The date where all the tasks took place
        :type date: datetime
        :param time_tracking_results: The results from the time tracking plugin
        :type time_tracking_results: dict
        :return: void
        """
        # element to group by
        grouping_fn = lambda x: x['description']

        # sort the elements (groupby needs them sorted)
        elements = sorted(time_tracking_results, key=grouping_fn)
        groups = itertools.groupby(elements, grouping_fn)
        res = [(r[0], sum([item['seconds'] for item in r[1]])) for r in groups]

        company = CompaniesMgr.get_company(company_id)
        for tt_task in res:
            try:
                task = company.tasks.where(Task.date == date, Task.description == tt_task[0]).get()
            except:
                task = Task()
                task.company = company
                task.date = date
                task.description = tt_task[0]

            task.time_spent_seconds = tt_task[1]
            task.save()

    @staticmethod
    def trigger_notifications(company_id):
        company = CompaniesMgr.get_company(company_id)

        for nplugin in company.notification_plugins:
            plugin = PluginsManager.get_notification_plugin(nplugin['notification_plugin'],
                                                            **nplugin['notification_data'])
            plugin.execute_if_it_has_to(company)


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
        return PluginsManager.get_object(name, 'time_tracking', **kwargs)

    @staticmethod
    def get_notification_plugin(name, **kwargs):
        """

        :param name: The name (with the module name) of the plugin to use
        :param kwargs: Values to use on the plugin creation
        :return: An instance of the plugin
        :rtype: BaseNotificationPlugin
        """
        return PluginsManager.get_object(name, 'notification', **kwargs)