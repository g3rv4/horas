from abc import ABCMeta, abstractmethod
from business_logic.models import Company

class BaseNotificationPlugin(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_if_it_has_to(self, company):
        """ Executes the notification if it has to

        It's the plugin's responsibility to know if it should execute or not

        :param company: The company to send the notifications to
        :type company: Company
        :return: void
        """
        pass