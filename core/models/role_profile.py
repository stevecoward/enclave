from peewee import *
from core.models.db import BaseModel
from core.models.puppet import Puppet
from helpers import Logger

class RoleProfile(BaseModel):
    id = IntegerField(primary_key=True)
    puppet = ForeignKeyField(Puppet, backref='puppet')
    name = CharField(null=True)
    properties = CharField(null=True)
    created = DateTimeField()
    updated = DateTimeField(null=True)

    def bootstrap(self):
        super(RoleProfile, self).bootstrap()
