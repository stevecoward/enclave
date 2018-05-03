from peewee import *
from core.models.db import BaseModel

class VpsInfo(BaseModel):
    id = IntegerField(primary_key=True)
    hash = CharField(unique=True)
    vps = CharField(null=True)
    api_key = CharField(null=True)
    secret_key = CharField(null=True)
    created = DateTimeField()

    def bootstrap(self):
        super(VpsInfo, self).bootstrap()