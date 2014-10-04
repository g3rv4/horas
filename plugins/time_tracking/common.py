from abc import ABCMeta, abstractmethod
from business_logic.models import Task, Company
import datetime

class BaseTimeTrackingPlugin(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def update_tasks_since(self, company, date):
        """ Updates all the tasks since the given date for the given company

        :param company: The company to update
        :type company: Company
        :param date: The date to start checking the times
        :type date: datetime.date
        :return: List of the tasks updated
        :rtype: [Task]
        """
        pass
