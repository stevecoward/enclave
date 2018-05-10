from db import database, BaseModel
from puppet import Puppet
from vps_info import VpsInfo
from role import Role
from role_profile import RoleProfile

enclave_tables = [Puppet, VpsInfo, Role, RoleProfile]
