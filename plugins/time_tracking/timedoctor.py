from base import BaseTimeTrackingPlugin


class TimeDoctorPlugin(BaseTimeTrackingPlugin):
    def __init__(self, username, password):
        super(TimeDoctorPlugin, self).__init__()
        self.username = username
        self.password = password

