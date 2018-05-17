from peewee import *
from delorean import Delorean
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

    @staticmethod
    def update_existing_or_create(puppet_id, profile):
        existing_profile = RoleProfile.select().where(RoleProfile.puppet_id == puppet_id).first()
        if existing_profile:
            existing_profile.name = profile.name
            existing_profile.properties = '|'.join(['{}:{}'.format(key, val) for key, val in profile.properties.iteritems()])
            existing_profile.updated = Delorean().datetime
            existing_profile.save()
        else:
            profile_record = RoleProfile(puppet_id=puppet_id, name=profile.name, \
                properties='|'.join(['{}:{}'.format(key, val) for key, val in profile.properties.iteritems()]),
                created=Delorean().datetime,
            )
            profile_record.save()