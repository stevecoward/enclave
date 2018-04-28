from peewee import *
from core.models.db import BaseModel

class Puppet(BaseModel):
    id = IntegerField(primary_key=True)
    vps = CharField(null=True)
    uuid = CharField(null=True)
    name = CharField(null=True)
    ram = IntegerField(null=True)
    cpu = IntegerField(null=True)
    disk = IntegerField(null=True)
    ip = CharField(null=True)
    created = DateTimeField()
    updated = DateTimeField(null=True)
