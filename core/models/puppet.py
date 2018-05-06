from peewee import *
from core.models.db import BaseModel
from core.models.vps_info import VpsInfo
from core.models.role import Role


class Puppet(BaseModel):
    vps_info = ForeignKeyField(VpsInfo, backref='vps_info')
    role = ForeignKeyField(Role, backref='role')

    id = IntegerField(primary_key=True)
    uuid = CharField(null=True)
    name = CharField(null=True)
    ram = IntegerField(null=True)
    cpu = IntegerField(null=True)
    disk = IntegerField(null=True)
    ip = CharField(null=True)
    created = DateTimeField()
    updated = DateTimeField(null=True)

    def bootstrap(self):
        super(Puppet, self).bootstrap()
