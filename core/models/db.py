from os.path import expanduser
from peewee import *

database = SqliteDatabase('{}/.enclave/enclave.db'.format(expanduser('~')))


class BaseModel(Model):
    def bootstrap(self):
        pass

    class Meta:
        database = database
