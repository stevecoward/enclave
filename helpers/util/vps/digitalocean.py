import json
import uuid
import hashlib
from delorean import Delorean
from helpers.log import Logger
from helpers.protocols.http.client import Client as HttpClient
from core.models import Puppet, VpsInfo, Role

class DigitalOceanVps():
    
    def __init__(self, api_key):
        client = HttpClient('api.digitalocean.com', 443, debug=False)
        client.set_header('Content-Type', 'application/json')
        client.set_header('Authorization', 'Bearer {}'.format(api_key))
        self.api_key = api_key
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

    def get_droplets(self):
        status, droplets_blob = self.client.get('/v2/droplets')
        if status == 200:
            droplets = json.loads(droplets_blob)
            if len(droplets['droplets']):
                vps_record = VpsInfo.select().where(VpsInfo.api_key == self.api_key).first()
                Logger.log('found {} droplets for vps: {}...'.format(len(droplets['droplets']), vps_record.hash[:5]), 'success')
                for droplet in droplets['droplets']:
                    puppet_ip = None
                    if len(droplet['networks']['v4']) > 0:
                        puppet_ip = droplet['networks']['v4'][0]['ip_address']

                    record = Puppet.select().where(Puppet.uuid == droplet['id']).first()
                    if not record:
                        vps_record = VpsInfo.select().where(VpsInfo.api_key == self.api_key).first()
                        null_role = Role.select().where(Role.name == 'null').first()
                        new_puppet = Puppet(vps='digitalocean', uuid=droplet['id'], \
                            name=droplet['name'], ram=droplet['memory'], cpu=droplet['vcpus'], \
                            disk=droplet['disk'], ip=puppet_ip, created=Delorean().datetime, \
                            vps_info_id=vps_record.id, role_id=null_role.id,
                        )
                        new_puppet.save()
                        Logger.log('added droplet {} to db'.format(droplet['id']), 'success')
                    else:
                        record.name = droplet['name']
                        record.ip = puppet_ip
                        record.updated = Delorean().datetime
                        record.save()
                        Logger.log('updated droplet {}'.format(droplet['name']), 'success')
        else:
            Logger.log('received http code: {} when getting droplets'.format(status), 'warning')

    def get_ip(self, id):
        ip_address = ''
        status, droplet = self.client.get('/v2/droplets/{}'.format(id))
        if status == 404:
            Logger.log('droplet not available, removing stale db record', 'info')
            Puppet.get(id).delete_instance()
        elif 200 <= status < 300:
            droplet = json.loads(droplet)
            ip_address = None
            if len(droplet['droplet']['networks']['v4']):
                ip_address = droplet['droplet']['networks']['v4'][0]['ip_address']
            else:
                Logger.log('droplet doesn\'t have an ip address yet...', 'info')
        return ip_address

    def delete_droplet(self, uuid):
        delete_status, delete_response = self.client.delete('/v2/droplets/{}'.format(uuid))
        if delete_status == 204:
            Logger.log('droplet {} has been successfully deleted'.format(uuid), 'success')
        else:
            Logger.log('delete task didn\'t return a 204, instead: {}'.format(delete_status), 'warning')

    def create_droplet(self, vps_hash, fingerprint):
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

            vps_record = VpsInfo.select().where(VpsInfo.api_key == self.api_key).first()
            
            puppet = Puppet.create(vps_info_id=vps_record.id, 
                uuid=create_response['droplet']['id'], 
                name=create_response['droplet']['name'], 
                ram=create_response['droplet']['memory'], 
                cpu=create_response['droplet']['vcpus'], 
                disk=create_response['droplet']['disk'], 
                created=create_response['droplet']['created_at'],
            )

            Logger.log('created digitalocean puppet:{}'.format(create_response['droplet']['id']), 'success')
