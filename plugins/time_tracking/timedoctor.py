from common import BaseTimeTrackingPlugin


class TimeDoctorPlugin(BaseTimeTrackingPlugin):
    def __init__(self, username, password):
        super(TimeDoctorPlugin, self).__init__()
        self.username = username
        self.password = password

    def update_tasks_since(self, company, date):
        res = []

        pass