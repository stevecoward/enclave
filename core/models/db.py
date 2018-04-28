from os.path import expanduser
from peewee import *

database = SqliteDatabase('{}/.enclave/enclave.db'.format(expanduser('~')))

class BaseModel(Model):
    class Meta:
        database = database
