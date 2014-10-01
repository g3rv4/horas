from abc import ABCMeta, abstractmethod


class BaseTimeTrackingPlugin(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_daily_report(self, date):
        pass


class DailyReport(object):
    def __init__(self, date):
        self.date = date
        self.tasks = []

    @property
    def total_in_seconds(self):
        return sum([t.time_in_seconds for t in self.tasks])


class Task(object):
    def __init__(self, description, time_in_seconds):
        self.description = description
        self.time_in_seconds = time_in_seconds
