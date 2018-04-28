from helpers.util.vps.digitalocean import DigitalOceanVps

class Vps():
    def __init__(self, name, api_key, secret_key='', *args, **kwargs):
        self.name = name
        self.api_key = api_key
        self.secret_key = secret_key
        if name == 'digitalocean':
            self.vps = DigitalOceanVps(self.api_key)
            self.vps.check_add_key(kwargs['pubkey'], kwargs['pubkey_fingerprint'])

    def create(self, *args, **kwargs):
        if self.name == 'digitalocean':
            self.vps.create_droplet(kwargs['pubkey_fingerprint'])
