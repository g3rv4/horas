from common import *


class TimeTrackingTestPlugin(BaseTimeTrackingPlugin):
    def __init__(self, responses):
        self.test_responses = responses

    def get_daily_report(self, date):
        res = DailyReport(date)
        if date in self.test_responses:
            for response in self.test_responses[date]:
                res.tasks.append(Task(response['description'], response['seconds']))

        return res
