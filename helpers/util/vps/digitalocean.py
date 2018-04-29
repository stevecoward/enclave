import json
import uuid
import hashlib
from helpers.log import Logger
from helpers.protocols.http.client import Client as HttpClient
from core.models.puppet import Puppet

class DigitalOceanVps():
    
    def __init__(self, token):
        client = HttpClient('api.digitalocean.com', 443, debug=False)
        client.set_header('Content-Type', 'application/json')
        client.set_header('Authorization', 'Bearer {}'.format(token))
        self.client = client

    def get_regions(self, check_cache=True):
        status, regions_blob = self.client.get('/v2/regions')
        regions = []
        try:
            regions = json.loads(regions_blob)
        except:
            Logger.log('error loading regions json blob', 'fail')
        self.regions = regions
        return regions

    def get_images(self, check_cache=True):
        status, images_blob = self.client.get('/v2/images?type=distribution')
        images = []
        try:
            images = json.loads(images_blob)
        except:
            Logger.log('error loading images json blob', 'fail')
        self.images = images
        return images

    def check_add_key(self, key, fingerprint):
        status, found_key = self.client.get('/v2/account/keys/{}'.format(fingerprint))
        if status == 404:
            Logger.log('pubkey not stored, adding...', 'info')
            addkey_status, addkey_response = self.client.post('/v2/account/keys', params={'name': 'enclave-pubkey','public_key': key}, content_type='json')
            if addkey_status == 201:
                Logger.log('pubkey added successfully', 'success')
        elif 200 <= status < 300:
            found_key = json.loads(found_key)
            if fingerprint == found_key['ssh_key']['fingerprint']:
                Logger.log('pubkey confirmed, ready to touch', 'info')

    def get_ip(self, id):
        ip_address = ''
        status, droplet = self.client.get('/v2/droplets/{}'.format(id))
        if status == 404:
            Logger.log('droplet not available, removing stale db record', 'info')
            Puppet.get(id).delete_instance()
        elif 200 <= status < 300:
            droplet = json.loads(droplet)
            ip_address = droplet['droplet']['networks']['v4'][0]['ip_address']
        return ip_address

    def create_droplet(self, fingerprint):
        create_status, create_response = self.client.post('/v2/droplets', params={
            'name': '{}'.format(uuid.uuid4()),
            'region': 'nyc3',
            'size': 's-1vcpu-1gb',
            'image': 'debian-9-x64',
            'ssh_keys': [fingerprint],
            'tags': ['enclave-{}'.format(hashlib.sha1(fingerprint).hexdigest())],
        }, content_type='json')
        if create_status == 202:
            create_response = json.loads(create_response)
            
            puppet = Puppet.create(vps='digitalocean', 
                uuid=create_response['droplet']['id'], 
                name=create_response['droplet']['name'], 
                ram=create_response['droplet']['memory'], 
                cpu=create_response['droplet']['vcpus'], 
                disk=create_response['droplet']['disk'], 
                created=create_response['droplet']['created_at'],
            )

            Logger.log('created do puppet:{}'.format(create_response['droplet']['id']), 'success')
