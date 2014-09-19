from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, DateTimeField, IntegerField
import datetime

db = SqliteDatabase('horas.db')

class Company(Model):
    name = CharField()
    daily_email = CharField()
    jira_server = CharField(default=None)
    jira_username = CharField(default=None)
    jira_password = CharField(default=None)
    time_tracking_plugin = CharField()


    class Meta:
        database = db


class ReportLine(Model):
    ticket_number = CharField(default=None)
    time_spent_seconds = IntegerField()


    class Meta:
        database = db


class Report(Model):
    company = ForeignKeyField(Company, related_name='successful_executions')
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

