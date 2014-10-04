from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, IntegerField, DateField, DateTimeField
import datetime
import pickle

db = SqliteDatabase('horas.db')


class Company(Model):
    name = CharField()
    notification_plugins_str = CharField()
    time_tracking_plugin = CharField()
    time_tracking_data_str = CharField()
    timezone = CharField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    @property
    def notification_plugins(self):
        return pickle.loads(self.notification_plugins_str)

    @notification_plugins.setter
    def notification_plugins(self, value):
        self.notification_plugins_str = pickle.dumps(value)

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
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        database = db
