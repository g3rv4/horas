from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, IntegerField, DateField
import datetime
import pickle

db = SqliteDatabase('horas.db')


class Company(Model):
    name = CharField()
    daily_email = CharField()
    issue_tracking_plugin = CharField(null=True, default=None)
    issue_tracking_data_str = CharField(null=True, default=None)
    time_tracking_plugin = CharField()
    time_tracking_data_str = CharField()

    @property
    def issue_tracking_data(self):
        return pickle.loads(self.issue_tracking_data_str)

    @issue_tracking_data.setter
    def issue_tracking_data(self, value):
        self.issue_tracking_data_str = pickle.dumps(value)

    @property
    def time_tracking_data(self):
        return pickle.loads(self.time_tracking_data_str)

    @time_tracking_data.setter
    def time_tracking_data(self, value):
        self.time_tracking_data_str = pickle.dumps(value)

    class Meta:
        database = db


class Task(Model):
    company = ForeignKeyField(Company, related_name='tasks')
    date = DateField()
    description = CharField()
    time_spent_seconds = IntegerField()

    class Meta:
        database = db
