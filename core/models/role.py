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
                Logger.log(
                    'bootstrap:role> added \'{}\' to db'.format(role), 'success')
            else:
                Logger.log(
                    'bootstrap:role> \'{}\' exists, skipping...'.format(role), 'info')

    @staticmethod
    def update_puppet_role(puppet, new_role_name):
        old_puppet_role = puppet.role.name
        new_role = Role.select().where(
            Role.name == new_role_name).first()
        Logger.log('puppet: {} role: {} --> {}'.format(puppet.name,
                                                       old_puppet_role, new_role.name), 'success')
        puppet.role_id = new_role.id
        puppet.save()