from delorean import Delorean
from peewee import *
from core.models.db import BaseModel
from helpers import Logger

class Role(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    created = DateTimeField()
    updated = DateTimeField(null=True)

    def bootstrap(self):
        super(Role, self).bootstrap()

        roles = ['c2', 'redir', 'null']
        for role in roles:
            if not self.select().where(Role.name == role):
                self.name = role
                self.created = Delorean().datetime
                self.save()
                Logger.log('bootstrap:role> added \'{}\' to db'.format(role), 'success')
            else:
                Logger.log('bootstrap:role> \'{}\' exists, skipping...'.format(role), 'info')
