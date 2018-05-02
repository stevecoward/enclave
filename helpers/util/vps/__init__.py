from helpers.util.vps.digitalocean import DigitalOceanVps

class Vps():
    def __init__(self, name, api_key, secret_key='', *args, **kwargs):
        self.name = name
        self.api_key = api_key
        self.secret_key = secret_key
        if name == 'digitalocean':
            self.vps = DigitalOceanVps(self.api_key)
            # TODO - maybe don't need to call this on every init? doesnt need to be
            # called everywhere. it definitely needs to be called on first run.
            # self.vps.check_add_key(kwargs['pubkey'], kwargs['pubkey_fingerprint'])

    def create(self, *args, **kwargs):
        if self.name == 'digitalocean':
            self.vps.create_droplet(kwargs['vps'], kwargs['pubkey_fingerprint'])

    def delete(self, *args, **kwargs):
        if self.name == 'digitalocean':
            self.vps.delete_droplet(kwargs['uuid'])

    def refresh(self, *args, **kwargs):
        if self.name == 'digitalocean':
            self.vps.get_droplets()
