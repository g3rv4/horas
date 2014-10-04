from common import *


class TimeTrackingTestPlugin(BaseTimeTrackingPlugin):
    def __init__(self, responses):
        self.test_responses = responses

    def update_tasks_since(self, company, date):
        raise Exception()
