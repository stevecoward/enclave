from db import database, BaseModel
from puppet import Puppet
from vps_info import VpsInfo
from role import Role

enclave_tables = [Puppet, VpsInfo, Role]
