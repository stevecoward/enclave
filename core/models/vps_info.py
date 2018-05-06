from peewee import *
from core.models.db import BaseModel
from helpers import Logger


class VpsInfo(BaseModel):
    id = IntegerField(primary_key=True)
    hash = CharField(unique=True)
    vps = CharField(null=True)
    api_key = CharField(null=True)
    secret_key = CharField(null=True)
    created = DateTimeField()

    def bootstrap(self):
        super(VpsInfo, self).bootstrap()

        inital_data = [{
            'hash': '6cd2d12c28a32021bd306abe4c2ccd9371dd33e6',
            'vps': 'digitalocean',
            'api_key': 'edf9c80806e0ea622f581b0d3e1990ec85e8e6b2f1b1f78d299cca675368b7a7',
            'created': '2018-05-02 21:53:39.804902+00:00',
        }, {
            'hash': '4b4ee5bba73438ef90d0972da66658af6309652d',
            'vps': 'digitalocean',
            'api_key': '81671281b8250b271003124319fe4a712b37d43250025edc334b180ea4d7a8bb',
            'created': '2018-05-02 21:53:39.804902+00:00',
        }]

        for record in inital_data:
            if not self.select().where(VpsInfo.hash == record['hash']):
                self.hash = record['hash']
                self.vps = record['vps']
                self.api_key = record['api_key']
                self.created = record['created']
                self.save()
                Logger.log('bootstrap:vps_info> added \'{}\' to db'.format(
                    record['hash']), 'success')
            else:
                Logger.log('bootstrap:vps_info> \'{}\' exists, skipping...'.format(
                    record['hash']), 'info')
